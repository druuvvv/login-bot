from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
import cv2 , time
import numpy as np
import bfs
import os
from progress.bar import Bar
from dotenv import load_dotenv
load_dotenv()
driver = webdriver.Chrome()
successCount = 0
attempts = 1000
driver.set_window_size(1920,1080)
with Bar('Effieciency... ', max = 100) as bar:
    for i in range(1,attempts+1):
        try:
            driver.get(os.getenv("URL"))
            login = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//a[text()=' LOGIN ']")))
            login.click()
            username = driver.find_element(By.XPATH,  '//*[@formcontrolname="userid"]')
            username.send_keys(os.getenv("USER_NAME"))
            time.sleep(0.66)
            password = driver.find_element(By.XPATH,  '//*[@formcontrolname="password"]')
            password.send_keys(os.getenv("PASSWORD"))
            time.sleep(0.66)
            captcha_image_selector = '.captcha-img'
            captcha_image = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, captcha_image_selector)))
            captcha_image.screenshot('captcha.png')
            img = cv2.imread('captcha.png', cv2.IMREAD_COLOR)
            c_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            c_gray = 255 - c_gray
            kernel = np.ones((3,3),np.uint8)
            out = cv2.medianBlur(c_gray,3)
            new_array = np.where(out < 180 , 0 , out)
            newer_array = np.where(new_array >=180 , 255 , new_array)
            out = bfs.removeIsland(newer_array, 30)
            out = cv2.medianBlur(out,3)
            captcha_text = pytesseract.image_to_string(out)
            if(len(captcha_text)<2):
                time.sleep(0.5)
                raise exceptions.NoSuchElementException
            captcha_field = driver.find_element(By.ID, 'captcha')
            captcha_field.send_keys(captcha_text.strip())
            login_button = driver.find_element(By.XPATH,  "//button[text()='SIGN IN']")
            time.sleep(3.3) 
            login_button.click()
            time.sleep(2)
            driver.find_element(By.XPATH,  "//div[text()='Bad credentials']")
            cv2.imwrite(f"captchas/{captcha_text.strip()}.png", img)
            successCount += 1
        except exceptions.UnexpectedAlertPresentException as e:
            print("I got stuck bitch run it slower could not fill the fucking field")
        except exceptions.NoSuchElementException as e:
            print(captcha_text)
        finally:
            efficiency = successCount/i
            bar.goto(efficiency*100)


print("Efficiency: ",efficiency*100,"%")
driver.quit()
