from browsermobproxy import Server
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
import json
import time
from get_answer import GetAnswer
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

USERID = os.environ.get('USERID')
PASSWORD = os.environ.get('PASSWORD')
'''크롬 로그 requests 만들기'''
caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}
'''윗 두줄은 실행파일 최상단에 위치하게 함'''
class SafeEdu:
    def __init__(self):
        self.get_answer = GetAnswer()
        self.service = Service(executable_path=r'.\chromedriver-win64\chromedriver.exe')
        chrome_options = Options()
        # chrome_options.add_argument("--auto-open-devtools-for-tabs")
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})  # 필수

        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.open_site()
        self.logs = None

    def open_site(self):
        self.driver.get('https://corp.edukisa.or.kr/home.do#')
        self.driver.maximize_window()
        time.sleep(2)

    def zoom_out(self):
        time.sleep(0.1)
        self.driver.execute_script("document.body.style.zoom='75%'")
        time.sleep(0.1)
    def zoom_in(self):
        time.sleep(0.1)
        self.driver.execute_script("document.body.style.zoom='100%'")
        time.sleep(0.1)

    def log_in(self):
        global USERID
        global PASSWORD
        try:
            self.input('//*[@id="rgst_num1"]', '8148500288')
            self.click('//*[@id="login_form_box"]/a')
            self.input('//*[@id="user_id"]', USERID)      # for user : ID
            self.input('//*[@id="user_pw"]', PASSWORD)      # for user : PW
            self.click('//*[@id="loginForm"]/a[1]')
            self.zoom_out()

            self.click('//*[@id="b2ccStuContId"]/div/div[2]/a')
            self.zoom_out()
            self.click('//*[@id="eduaplList"]/li/div/div[4]/button[1]')
            return True
        except Exception as e:
            print(e)
            return False

    def find_next_study_button(self):
        try:
            time.sleep(1)
            self.zoom_out()
            target_argument = 'stdEdu'
            button_1st = self.driver.find_element(By.XPATH, '//*[@id="trnAList"]/tr[2]/td[5]/button')
            self.driver.execute_script("arguments[0].scrollIntoView(true);", button_1st)

            buttons = self.driver.find_elements(By.XPATH, "//button[@type='button']")

            for button in buttons:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(0.5)
                self.zoom_out()
                onclick_attribute = button.get_attribute('onclick')
                print(onclick_attribute)
                if onclick_attribute:
                    if (target_argument in onclick_attribute) and ('N' in onclick_attribute):
                        print(f'학습하기 버튼을 찾았습니다: {button}')
                        button.click()
                        time.sleep(0.5)
                        self.zoom_in()
                        self.click('//*[@id="play"]')
                        self.wait_for_progress_and_click()
                        break
                    elif ("fnChkTestPsb" in onclick_attribute) and ('N' in onclick_attribute):
                        print(f'시험보기 버튼을 찾았습니다: {button}')
                        button.click()
                        time.sleep(0.8)
                        self.zoom_out()
                        time.sleep(1)
                        self.click('//*[@id="myclass-edu-attn-window"]/div[1]/label/span')
                        time.sleep(1)
                        self.click('//*[@id="myclass-edu-attn-window"]/div[2]/div/button[2]')
                        time.sleep(1)
                        # self.get_test_data()
                        self.get_answer_list()
                        self.submit_test()
                        time.sleep(0.5)
                        time.sleep(100)
        except Exception as e:
            print(e)

    def get_test_data(self):
        self.logs = self.driver.get_log("performance")

        for log in self.logs:
            if "insert_edu_exam_qst.do" in log["message"]:
                network_message = json.loads(log["message"])
                method = network_message["message"]["method"]

                if method == "Network.responseReceived":
                    response_data = network_message["message"]["params"]["response"]
                    print("Response Data:", response_data)

    def submit_test(self):
        ul = self.driver.find_element(By.ID, "examList")
        li_list = ul.find_elements(By.TAG_NAME, "li")

        answer_list = self.get_answer_list()
        for index, li in enumerate(li_list):
            exam_id = li.get_attribute("id")
            exam_cont = li.find_element(By.XPATH,f'//*[@id="testExamNum_{exam_id}"]/div[2]')
            exam_btn_list = exam_cont.find_element(By.XPATH,f'//*[@id="testExamNum_{exam_id}"]/div[2]/div')
            answer_button = exam_btn_list.find_element(By.ID,f'examNum_{exam_id}_{answer_list[index]}')
            print(answer_button.text)


        pass
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
        temp = input("Copy json response in response.txt")  # wait until copy json answer
        self.get_answer.run()
        ans_list = self.get_answer.answer_list
        # click answer
        return ans_list

    def click(self, x_path=''):
        try:
            click_element = self.driver.find_element(By.XPATH, x_path)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                       click_element)
            click_element.click()
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Failed to click on element: {e}")
            return False

    def click_id(self, id=''):
        try:
            click_element = self.driver.find_element(By.ID, id)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                       click_element)
            click_element.click()
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Failed to click on element: {e}")
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
    SE.zoom_out()
    if SE.log_in():
        SE.find_next_study_button()
        # SE.find_next_study_button()

    time.sleep(30)
    SE.quit()
