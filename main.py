from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import json
import time
from get_answer import GetAnswer
from dotenv import load_dotenv
import os
import inspect

# load .env
load_dotenv()
USERID = os.environ.get("USERID")
PASSWORD = os.environ.get("PASSWORD")
SITEURL = os.environ.get("SITEURL")
BUSINESS_NUM = os.environ.get("BUSINESS_NUM")

'''크롬 로그 requests 만들기'''
caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}


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
        self.actions = ActionChains(self.driver)  # 스크롤 위치 조정 가능 객체
        self.debug_mode = False

    def open_site(self):
        global SITEURL
        self.driver.get(SITEURL)
        self.driver.maximize_window()
        time.sleep(2.5)

    def zoom_out(self):
        time.sleep(1)
        self.driver.execute_script("document.body.style.zoom='75%'")
        time.sleep(1)

    def zoom_in(self):
        time.sleep(1)
        self.driver.execute_script("document.body.style.zoom='100%'")
        time.sleep(1)

    def log_in(self):
        global USERID
        global PASSWORD
        global BUSINESS_NUM
        try:
            self.input('//*[@id="rgst_num1"]', BUSINESS_NUM)
            self.click('//*[@id="login_form_box"]/a')
            self.input('//*[@id="user_id"]', USERID)  # for user : ID
            self.input('//*[@id="user_pw"]', PASSWORD)  # for user : PW
            self.click('//*[@id="loginForm"]/a[1]')
            self.zoom_out()
        except Exception as e:
            self.print_error_msg(inspect.currentframe().f_code.co_name, f"Fail to login. {e}")
            return False

    def find_edu(self):
        try:
            if not self.click('//*[@id="b2ccStuContId"]/div/div[2]/a'):
                raise False
            self.zoom_out()
            self.click('//*[@id="eduaplList"]/li/div/div[4]/button[1]')
            return True
        except Exception as e:
            self.print_error_msg(inspect.currentframe().f_code.co_name, f"Fail to find lecture. {e}")
            return False

    def find_next_study_button(self):
        try:
            time.sleep(1)
            target_argument = 'stdEdu'
            buttons = self.driver.find_element(By.ID,"trnAList").find_elements(By.TAG_NAME,"button")
            self.zoom_out()
            study_or_test_flag = False
            for index,button in enumerate(buttons):
                time.sleep(1)
                onclick_attribute = button.get_attribute('onclick')
                if onclick_attribute:
                    if (target_argument in onclick_attribute) and ('N' in onclick_attribute):
                        print(f'학습하기 버튼을 찾았습니다: {button}')
                        study_or_test_flag = True
                        try:
                            self.actions = ActionChains(self.driver)
                            self.actions.move_to_element(button).perform()
                        except Exception as E:
                            for i in range(index):
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", buttons[i])
                                time.sleep(0.2)
                        button.click()
                        time.sleep(1)
                        self.zoom_out()
                        self.click('//*[@id="play"]')
                        self.wait_for_progress_and_click()
                        break
                    elif ("fnChkTestPsb" in onclick_attribute) and button.accessible_name == "시험보기":
                        print(f'시험보기 버튼을 찾았습니다: {button}')
                        try:
                            self.actions = ActionChains(self.driver)
                            self.actions.move_to_element(button).perform()
                        except Exception as E:
                            for i in range(index):
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", buttons[i])
                                time.sleep(0.2)
                        button.click()
                        time.sleep(1)
                        self.zoom_out()
                        time.sleep(1)
                        self.click('//*[@id="myclass-edu-attn-window"]/div[1]/label/span')
                        time.sleep(1)
                        self.click('//*[@id="myclass-edu-attn-window"]/div[2]/div/button[2]')
                        time.sleep(1)
                        self.get_network_log()
                        self.submit_test()
                        time.sleep(1)
                        time.sleep(2.5)
                        study_or_test_flag = True

            return study_or_test_flag
        except Exception as e:
            self.print_error_msg(inspect.currentframe().f_code.co_name, e)
            self.driver.refresh()
            return False

    def get_network_log(self):
        time.sleep(1)
        self.logs = self.driver.get_log("performance")

        for log in self.logs:
            if "insert_edu_exam_qst.do" in log["message"]:
                network_message = json.loads(log["message"])
                method = network_message["message"]["method"]

                if method == "Network.responseReceived":
                    request_id = network_message["message"]["params"]["requestId"]
                    resp = self.driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
                    data = resp["body"]
                    print(type(data))
                    with open("response.txt", 'w', encoding='utf-8') as file:
                        file.write(data)
        time.sleep(1)
        print("response write finished")

    def submit_test(self):
        ul = self.driver.find_element(By.ID, "examList")
        li_list = ul.find_elements(By.TAG_NAME, "li")
        count = 0
        answer_list = self.get_answer_list()
        answer_list[-1] = 1 #오답 만들기
        print("답을 받아왔습니다.", answer_list)
        for index, li in enumerate(li_list):
            # exam_id = li.get_attribute("id")
            exam_cont = li.find_element(By.CLASS_NAME, f'exam-cont')
            exam_btn_list = exam_cont.find_element(By.CLASS_NAME, f'exam-optlst')
            label_list = exam_btn_list.find_elements(By.TAG_NAME, "label")
            ans_btn = label_list[answer_list[index]]
            self.actions = ActionChains(self.driver)
            self.actions.move_to_element(ans_btn).perform()
            time.sleep(1)
            ans_btn.click()
            count += 1

        if count == 7:
            result_btn = self.driver.find_element(By.ID, "examRlt")
            self.actions = ActionChains(self.driver)
            self.actions.move_to_element(result_btn).perform()
            result_btn.click()
            try:
                # 첫 번째 알람 수락
                alert = Alert(self.driver)
                alert.accept()
                print("첫 번째 알람 수락")
                time.sleep(1)
                # 두 번째 알람 수락
                alert = Alert(self.driver)  # error 발생
                alert.accept()
                time.sleep(1)
                print("두 번째 알람 수락")
                print("제출 성공")
            except Exception as e:
                self.print_error_msg(inspect.currentframe().f_code.co_name, e)
                self.driver.refresh()

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

            close_button = self.driver.find_element(By.XPATH, "/html/body/div[11]/div[1]/div/button/span")
            print("학습을 종료합니다.")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                self.actions = ActionChains(self.driver)
                self.actions.move_to_element(close_button)
                close_button.click()
                print('Close 버튼을 클릭했습니다.')
            except Exception as err:
                self.print_error_msg(inspect.currentframe().f_code.co_name, f"close button click fail. {err}")
                self.driver.refresh()
        except Exception as e:
            self.print_error_msg(inspect.currentframe().f_code.co_name, e)

    def get_answer_list(self):
        # temp = input("Copy json response in response.txt")  # wait until copy json answer
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
            if self.debug_mode:
                self.print_error_msg(inspect.currentframe().f_code.co_name, e)
            return False

    def click_id(self, id=''):
        try:
            click_element = self.driver.find_element(By.ID, id)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                       click_element)
            click_element.click()
            time.sleep(0.5)
        except Exception as e:
            if self.debug_mode:
                self.print_error_msg(inspect.currentframe().f_code.co_name, e)
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

    @staticmethod
    def print_error_msg(func_name, msg):
        print(f"[ERROR] {func_name} : {msg}")


if __name__ == "__main__":
    SE = SafeEdu()
    if SE.log_in():
        if SE.find_edu():
            a = True
            while a:
                a = SE.find_next_study_button()
            # SE.find_next_study_button()

    time.sleep(30)
    SE.quit()
