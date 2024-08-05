from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
import cv2
import numpy as np
import bfs
import os
from progress.bar import Bar
from dotenv import load_dotenv
load_dotenv()
driver = webdriver.Chrome()
successCount = 0
with Bar('Working... ', max = 50) as bar:
    for i in range(2):
        driver.get(os.getenv("URL"))
        username = driver.find_element(By.ID, os.getenv("USER_NAME_TAG_ID"))
        username.send_keys(os.getenv("USER_NAME"))
        password = driver.find_element(By.ID, os.getenv("PASSWORD_TAG_ID"))
        password.send_keys(os.getenv("PASSWORD"))
        captcha_image_selector = '#imgCaptcha'
        captcha_image = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, captcha_image_selector)))
        captcha_image.screenshot('captcha.png')
        img = cv2.imread('captcha.png', cv2.IMREAD_COLOR)
        c_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        kernel = np.ones((3,3),np.uint8)
        out = cv2.medianBlur(c_gray,3)
        new_array = np.where(out < 180 , 0 , out)
        newer_array = np.where(new_array >=180 , 255 , new_array)
        out = bfs.removeIsland(newer_array, 30)
        out = cv2.medianBlur(out,3)
        captcha_text = pytesseract.image_to_string(out)
        if(len(captcha_text)<6):
            continue
        captcha_field = driver.find_element(By.ID, 'ctl00_dpPH_txtVerificationCode')
        captcha_field.send_keys(captcha_text.strip())
        login_button = driver.find_element(By.ID, 'ctl00_dpPH_btnLogin') 
        login_button.click()
        if(driver.current_url == os.getenv("SUCCESS_URL")): 
            cv2.imwrite(f"captchas/{captcha_text}.png", img)
            successCount += 1
        bar.next()
efficiency = successCount/50
print("Efficiency: ",efficiency*100,"%")
driver.quit()
