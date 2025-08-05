# -*- coding: utf-8 -*-
"""
This module provides a SafeEdu class to automate training playback and testing on a Safety Education platform.
It uses Selenium WebDriver to log in, navigate lectures, play learning videos, and submit tests automatically.

Features:
- Login using credentials stored in environment variables
- Navigate and select lectures
- Automatically find and click 'Study' or 'Test' buttons
- Monitor video progress and close upon completion
- Retrieve and save network logs related to exam questions
- Automatically answer and submit tests based on answers fetched via the GetAnswer class
- Handles alerts during test submission
"""
import os
import sys
import json
import time

from dotenv import load_dotenv
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from get_answer import GetAnswer

# load .env
load_dotenv()

# 크롬 로그 requests 만들기
caps = DesiredCapabilities.CHROME
caps['goog:loggingPrefs'] = {'performance': 'ALL'}


class SafeEdu:

    def __init__(self):
        self.get_answer = GetAnswer()
        self.service = Service(executable_path=os.environ.get("CHROMEDRIVER_PATH"))
        chrome_options = Options()
        # chrome_options.add_argument("--auto-open-devtools-for-tabs")
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.open_site()
        time.sleep(2.5)
        self.logs = None
        self.actions = ActionChains(self.driver)  # 스크롤 위치 조정 가능 객체
        self.debug_mode = False

    def open_site(self):
        """
        Navigate to the SafeEdu site URL from environment variables,
        maximize the window and wait briefly for the page to load.
        """
        site_url = os.environ.get("SITEURL")
        self.driver.get(site_url)
        self.driver.maximize_window()

    def log_in(self) -> bool:
        """
        Log into SafeEdu using user ID, password, and business number from environment variables.
        Returns:
            bool: True if login succeeds, False otherwise.
        """
        try:
            self.input_str('//*[@id="rgst_num1"]', os.environ.get("BUSINESS_NUM").replace("-", ""))
            self.click('//*[@id="login_form_box"]/a')
            self.input_str('//*[@id="user_id"]', os.environ.get("USERID"))
            self.input_str('//*[@id="user_pw"]', os.environ.get("PASSWORD"))
            self.click('//*[@id="loginForm"]/a[1]')
            # self.zoom_out()
            return True
        except Exception as e:
            self.print_error_msg(self.log_in.__name__, str(e))
            return False

    def find_edu(self) -> bool:
        """
        Navigate to the lecture list and select the first available lecture.
        Returns:
            bool: True if lecture selection succeeds, False otherwise.
        """
        try:
            if not self.click('//*[@id="b2ccStuContId"]/div/div[2]/a'):
                return False
            self.zoom_out()
            self.click('//*[@id="eduaplList"]/li/div/div[4]/button[1]')
            return True
        except Exception as e:
            self.print_error_msg(self.find_edu.__name__, str(e))
            return False

    def move_to_element_safely(self, element: WebElement, index: int, buttons):
        """
        Attempts to move the mouse cursor to the specified element using ActionChains.
        If the movement fails, it scrolls through the buttons up to the given index
        to bring elements into view as a fallback.
        Args:
            element (WebElement): The target element to move to.
            index (int): The index up to which buttons should be scrolled into view on failure.
            buttons (list[WebElement]): List of button elements to scroll through if needed.
        """
        try:
            self.actions.move_to_element(element).perform()
            time.sleep(0.2)
        except Exception as err:
            if self.debug_mode:
                self.print_error_msg(self.move_to_element_safely.__name__, str(err))
            for i in range(index):
                self.driver.execute_script("arguments[0].scrollIntoView(true);", buttons[i])
                time.sleep(0.2)

    def handle_study_button(self, button: WebElement, index: int, buttons) -> bool:
        """
        Handles the process of clicking the 'study' button and managing the subsequent
        study session including starting the video and waiting for its completion.
        Args:
            button (WebElement): The study button element to click.
            index (int): The index of the current button in the list.
            buttons (list[WebElement]): The list of buttons available.
        Returns:
            bool: True if the study process was completed successfully, False otherwise.
        """
        self.print_debug_msg(self.handle_study_button.__name__,f'학습하기 버튼을 찾았습니다: {button}')
        self.move_to_element_safely(button, index, buttons)
        try:
            button.click()
            time.sleep(1)
            self.zoom_out()
            self.click('//*[@id="play"]')
            self.wait_for_progress_and_click()
            return True
        except Exception as e:
            self.print_error_msg(self.handle_study_button.__name__, str(e))
            return False

    def handle_test_button(self, button, index, buttons) -> bool:
        """
        Handles the process of clicking the 'test' button, managing test start,
        and submitting answers after retrieving necessary data.
        Args:
            button (WebElement): The test button element to click.
            index (int): The index of the current button in the list.
            buttons (list[WebElement]): The list of buttons available.
        Returns:
            bool: True if the test process and submission were completed successfully,
                  False otherwise.
        """
        self.print_debug_msg(self.handle_test_button.__name__, f'시험보기 버튼을 찾았습니다: {button}')
        self.move_to_element_safely(button, index, buttons)
        try:
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
            time.sleep(3.5)
            return True
        except Exception as e:
            self.print_error_msg(self.handle_test_button.__name__, str(e))
            return False

    def find_next_study_button(self) -> bool:
        """
        Search for the next available study or test button on the lecture page.
        Perform the necessary clicks and actions to start studying or testing.
        Returns:
            bool: True if a study/test session starts successfully, False otherwise.
        """
        try:
            time.sleep(1)
            target_argument = 'stdEdu'
            buttons = self.driver.find_element(By.ID, "trnAList").find_elements(By.TAG_NAME, "button")
            self.zoom_out()
            spinner = ['-', '\\', '|', '/']
            line = "Finding enabled button... It will take a few second..."
            for index, button in enumerate(buttons):
                sys.stdout.write("\r" + f"{line}{spinner[index%4]}")
                sys.stdout.flush()
                time.sleep(0.5)
                onclick_attribute = button.get_attribute('onclick')
                if onclick_attribute:
                    if (target_argument in onclick_attribute) and ('N' in onclick_attribute):   # "학습하기" 버튼
                        print("\nStart studying!")
                        if self.handle_study_button(button, index, buttons):
                            return True
                        break
                    if ("fnChkTestPsb" in onclick_attribute) and button.accessible_name == "시험보기":
                        print("\nStart the test!")
                        if self.handle_test_button(button, index, buttons):
                            return True
                        break
            self.driver.refresh()
            return False
        except Exception as e:
            self.print_error_msg(self.find_next_study_button.__name__, str(e))
            self.driver.refresh()
            return False

    def get_network_log(self):
        """
        Capture Chrome's performance logs to extract network responses
        related to exam question data and save them to 'response.txt'.
        """
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
                    self.print_debug_msg(self.get_network_log.__name__, f"Data type : {type(data)}")
                    with open("response.txt", 'w', encoding='utf-8') as file:
                        file.write(data)
        time.sleep(1)
        print("response write finished")

    def submit_test(self):
        """
        Automatically fill in answers for a test, submit it,
        and handle any alert dialogs during submission.
        """
        ul = self.driver.find_element(By.ID, "examList")
        li_list = ul.find_elements(By.TAG_NAME, "li")
        count = 0
        answer_list = self.get_answer_list()
        answer_list[-1] = 1 #오답 만들기
        self.print_debug_msg(self.submit_test.__name__, f"answer_list - {answer_list}")
        for index, li in enumerate(li_list):
            # exam_id = li.get_attribute("id")
            exam_cont = li.find_element(By.CLASS_NAME, 'exam-cont')
            exam_btn_list = exam_cont.find_element(By.CLASS_NAME, 'exam-optlst')
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
                alert1 = Alert(self.driver)
                alert1.accept()
                print("첫 번째 알람 수락")
                time.sleep(3)
                # 두 번째 알람 수락
                alert2 = Alert(self.driver)  # error 발생
                alert2.accept()
                time.sleep(1)
                print("두 번째 알람 수락")
                print("제출 성공")
            except Exception as e:
                self.print_error_msg(self.submit_test.__name__, str(e))
                self.driver.refresh()

    def wait_for_progress_and_click(self):
        """
        Monitor the progress bar for a learning video,
        wait until completion, and then close the video player.
        """
        try:
            progress_bar = self.driver.find_element(By.ID, "progress-bar")
            max_value = int(progress_bar.get_attribute('max'))
            bar_length = 40
            while True:
                current_value = int(progress_bar.get_attribute('value'))
                percent = current_value / max_value
                filled_len = int(bar_length * percent)
                bar = '█' * filled_len + '-' * (bar_length - filled_len)
                line = f"Progress: |{bar}| {current_value}/{max_value} ({percent*100:.2f}%)"
                sys.stdout.write("\r" + line.ljust(80))
                sys.stdout.flush()
                if current_value >= max_value:
                    print('Video is done.')
                    break
                time.sleep(1)
            print()
            close_button = self.driver.find_element(By.XPATH, "/html/body/div[11]/div[1]/div/button/span")
            print("학습을 종료합니다.")
            try:
                self.driver.execute_script("arguments[0].scrollIntoView(true);", close_button)
                self.actions = ActionChains(self.driver)
                self.actions.move_to_element(close_button)
                close_button.click()
                print('Close 버튼을 클릭했습니다.')
            except Exception as err:
                self.print_error_msg(self.wait_for_progress_and_click.__name__,
                                     f"Close button click fail. {err}")
                self.driver.refresh()
        except Exception as e:
            self.print_error_msg(self.wait_for_progress_and_click.__name__, str(e))

    def get_answer_list(self) -> list:
        """
        Fetch the list of answers using the GetAnswer instance.
        Returns:
            list: List of answer indices.
        """
        self.get_answer.run()
        ans_list = self.get_answer.answer_list
        return ans_list

    def zoom_out(self):
        """
        Zoom out the page to 75% scale to ensure UI elements fit properly.
        """
        self.driver.execute_script("document.body.style.zoom='75%'")
        time.sleep(1)

    def zoom_in(self):
        """
        Reset page zoom to 100% (default size).
        """
        self.driver.execute_script("document.body.style.zoom='100%'")
        time.sleep(1)

    def click(self, x_path: str='') -> bool:
        """
        Find an element by XPath, scroll it into view, and click it.
        Args:
            x_path (str): XPath selector of the element to click.
        Returns:
            bool: True if click succeeds, False otherwise.
        """
        try:
            click_element = self.driver.find_element(By.XPATH, x_path)
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
                                       click_element)
            click_element.click()
            time.sleep(0.5)
            return True
        except Exception as e:
            if self.debug_mode:
                self.print_error_msg(self.click.__name__, str(e))
            return False

    def input_str(self, x_path: str='', input_st: str='') -> bool:
        """
        Find an input element by XPath, click it, and send keys.
        Args:
            x_path (str): XPath selector of the input element.
            input_st (str): String to input.
        Returns:
            bool: True if input succeeds, False otherwise.
        """
        try:
            click_element = self.driver.find_element(By.XPATH, x_path)
            click_element.click()
            click_element.send_keys(input_st)
            time.sleep(0.1)
            return True
        except Exception as e:
            self.print_error_msg(self.input_str.__name__, str(e))
            return False

    def print_debug_msg(self, func_name: str, msg: str):
        """
        Print debug message with the function name for debugging.
        Args:
            func_name (str): Name of the function.
            msg (str): The message to print.
        """
        if self.debug_mode:
            print(f"[DEBUG] {func_name}: {msg}")

    @staticmethod
    def print_error_msg(func_name: str, msg: str):
        """
        Print error message with the function name for debugging.
        Args:
            func_name (str): Name of the function where the error occurred.
            msg (str): The error message.
        """
        print(f"[ERROR] {func_name}: {msg}")


if __name__ == "__main__":
    SE = SafeEdu()
    if SE.log_in():
        if SE.find_edu():
            while True:
                ret = SE.find_next_study_button()
                if not ret:
                    print("Cannot find buttons.")
                    break
        else:
            print("Fail to find lecture.")
    else:
        print("Fail to login.")
    print("END")

    time.sleep(10)
    SE.driver.quit()
