from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
import json
import time
from get_answer import GetAnswer

USERID = ""
PASSWORD = ""

class SafeEdu:
    def __init__(self):
        self.get_answer = GetAnswer()
        self.service = Service(executable_path=r'.\chromedriver-win64\chromedriver.exe')
        chrome_options = Options()
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.open_site()

    def open_site(self):
        self.driver.get('https://corp.edukisa.or.kr/home.do#')
        self.driver.maximize_window()
        time.sleep(2)

    def log_in(self):
        global USERID
        global PASSWORD
        try:
            self.input('//*[@id="rgst_num1"]', '8148500288')
            self.click('//*[@id="login_form_box"]/a')
            self.input('//*[@id="user_id"]', USERID)      # for user : ID
            self.input('//*[@id="user_pw"]', PASSWORD)      # for user : PW
            self.click('//*[@id="loginForm"]/a[1]')
            self.click('//*[@id="b2ccStuContId"]/div/div[2]/a')
            self.click('//*[@id="eduaplList"]/li/div/div[4]/button[1]')
            return True
        except Exception as e:
            print(e)
            return False

    def find_next_study_button(self):
        try:
            time.sleep(1)
            target_argument = 'stdEdu'
            button_1st = self.driver.find_element(By.XPATH, '//*[@id="trnAList"]/tr[2]/td[5]/button')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button_1st)

            buttons = self.driver.find_elements(By.XPATH, "//button[@type='button']")

            for button in buttons:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)
                onclick_attribute = button.get_attribute('onclick')
                print(onclick_attribute)
                if onclick_attribute:
                    if (target_argument in onclick_attribute) and ('N' in onclick_attribute):
                        print(f'학습하기 버튼을 찾았습니다: {button}')
                        button.click()
                        time.sleep(0.5)
                        self.click('//*[@id="play"]')
                        self.wait_for_progress_and_click()
                        break
                    elif ("fnChkTestPsb" in onclick_attribute) and ('N' in onclick_attribute):
                        print(f'시험보기 버튼을 찾았습니다: {button}')
                        button.click()
                        time.sleep(0.5)
                        self.click('//*[@id="myclass-edu-attn-window"]/div[1]/label/span')
                        self.click('//*[@id="myclass-edu-attn-window"]/div[2]/div/button[2]')
                        time.sleep(0.5)
                        self.get_answer_list()
                        time.sleep(100)
        except Exception as e:
            print(e)

    def wait_for_progress_and_click(self):
        try:
            progress_bar = self.driver.find_element(By.ID, "progress-bar")
            max_value = int(progress_bar.get_attribute('max'))
            while True:
                current_value = int(progress_bar.get_attribute('value'))
                print(f'Progress: {current_value}/{max_value}')
                if current_value >= max_value:
                    print('Video is done.')
                    break
                time.sleep(1)

            close_button = self.driver.find_element(By.XPATH, '//*[@aria-label="Close"]')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
            close_button.click()
            print('Close 버튼을 클릭했습니다.')

        except Exception as e:
            print(f'오류 발생: {e}')

    def get_answer_list(self):
        temp = input("Copy json response in response.txt")
        self.get_answer.run()
        ans_list = self.get_answer.answer_list
        # click answer

    def click(self, x_path=''):
        try:
            click_element = self.driver.find_element(By.XPATH, x_path)
            self.driver.execute_script("arguments[0].scrollIntoView();", click_element)
            click_element.click()
            time.sleep(0.5)
        except:
            return False

    def input(self, x_path='', input=''):
        try:
            click_element = self.driver.find_element(By.XPATH, x_path)
            click_element.click()
            click_element.send_keys(input)
            time.sleep(0.1)
        except:
            return False

    def quit(self):
        time.sleep(5)
        self.driver.quit()


if __name__ == "__main__":
    SE = SafeEdu()
    if SE.log_in():
        SE.find_next_study_button()
        SE.find_next_study_button()

    time.sleep(30)
    SE.quit()
