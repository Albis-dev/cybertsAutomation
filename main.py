# simple div / button / radio object modification and POST / GET using Selenium
# tested in python 3.11 with selenium lastest version

TARGET_WEBPAGE = "https://www.cyberts.kr/cp/pvr/cpr/readCpPvrCarPrsecResveMainView.do"
REGISTRATION_ID = "110111" # PLACEHOLDER, MODIFY THIS AS YOU NEED
CAR_NUMBERS = [] 
CSV_COL_NAME_CAR_NUMBERS = "차량번호"
MAX_THREADS = 8 # trial and error as you need 


import concurrent.futures
from tqdm import tqdm
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException

# Function to process a single car number
def process_car(car_number):
    try:
        options = webdriver.ChromeOptions()
        # "Run Chrome in headless mode"
        options.add_argument("--no-sandbox") # bypass every security check
        options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
        options.add_argument("--headless")
        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 5)
    except Exception as e:
        return (car_number, "프로그램 오류 : " + str(e))
    
    try:
        driver.get(TARGET_WEBPAGE)
        driver.find_element(By.ID, "indvdlInfoAgre1").click()
        driver.find_element(By.ID, "txtCarNo").send_keys(car_number)
        driver.find_element(By.ID, "txtRegiNum").send_keys(REGISTRATION_ID)
        driver.find_element(By.ID, "btnSearch").click()
        wait.until(EC.invisibility_of_element_located((By.ID, "divProgressLoading")))
        result = driver.find_element(By.ID, "txtGuide").text.split(".")[0]
    except UnexpectedAlertPresentException as e:
        result = e.alert_text
    except Exception as e:
        result = "조회 실패"

        
    driver.quit()
    result = result.split("\n")[0]

    return (car_number, result)

if __name__ == "__main__":
    from tkinter import filedialog, dialog
    options = {
        "defaultextension": ".txt",
        "filetypes": [
            ("txt files", ".txt")
        ],
        "title": "txt 파일을 선택하세요",
    }

    txt_file = filedialog.askopenfilename(**options)

    # try parse csv file
    from csv import reader
    try:
        with open(txt_file, "r") as f:
            data = reader(f)
            # skip first row
            next(data)
            for row in data:
                CAR_NUMBERS.append(row[0])
    except:
        # show an error message
        dialog.showerror("오류", "파일이 유효하지 않습니다.")
        exit()

    results = [] # list of tuples (car_number, result message)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        future_to_car = {executor.submit(process_car, car_number): car_number for car_number in CAR_NUMBERS}

        # Use tqdm to create a progress bar
        with tqdm(total=len(CAR_NUMBERS)) as pbar:
            for future in concurrent.futures.as_completed(future_to_car):
                car_number = future_to_car[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Error processing car {car_number}: {e}")
                pbar.update(1)  # Update the progress bar

    # make a new dict based on the results
    results_dict = {}
    for result in results:
        results_dict[result[0]] = result[1]


    # delete result.txt if already exists

    if os.path.exists("result.txt"):
        os.remove("result.txt")
    with open("result.txt", "w") as f:
        # write results to result.txt
        for car_number in CAR_NUMBERS:
            result = results_dict[car_number]
            f.write(car_number + " " + result + "\n")







