from browsermobproxy import Server
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.webdriver import WebDriver
import json
import time


class SafeEdu:
    def __init__(self):
        self.service = Service(
            executable_path=r'C:\source\seyeong_draft\chromedriver-win64\chromedriver.exe')  # ChromeDriver 경로 지정
        chrome_options = Options()
        chrome_options.set_capability('loggingPrefs', {'performance': 'ALL'})
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)

        self.dev_tools, _ = self.driver.start_devtools()
        self.enable_network_monitoring()
        self.open_site()
        self.driver.execute_cdp_cmd("Performance.enable", {})

    def enable_network_monitoring(self):
        self.driver.execute_cdp_cmd('Network.enable', {})
        self.driver.request_interceptor = self.on_response

    def on_request(self, request):
        """요청이 보내질 때마다 호출되는 콜백 함수"""
        print(f"요청 URL: {request['url']}")

    def on_response(self, response):
        """네트워크 응답 처리"""
        if 'insert' in response['response']['url']:  # 응답 URL에 'insert' 포함 여부 확인
            try:
                # JSON 응답 데이터 출력
                data = response['response']
                if 'body' in data:
                    json_data = json.loads(data['body'])
                    print(f"Insert 데이터를 찾았습니다: {json_data}")
            except Exception as e:
                print(f"응답 처리 중 오류 발생: {e}")

    def open_site(self):
        self.driver.get('https://corp.edukisa.or.kr/home.do#')
        self.driver.maximize_window()
        time.sleep(2)

    def log_in(self):
        self.input('//*[@id="rgst_num1"]', '8148500288')
        self.click('//*[@id="login_form_box"]/a')
        self.input('//*[@id="user_id"]', 'id')      # for user : ID
        self.input('//*[@id="user_pw"]', 'pw')      # for user : PW
        self.click('//*[@id="loginForm"]/a[1]')

    def enter_classroom(self):
        self.click('//*[@id="b2ccStuContId"]/div/div[2]/a')
        self.click('//*[@id="eduaplList"]/li/div/div[4]/button[1]')

    def find_next_study_button(self):
        try:
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
                        break
                    elif ("fnChkTestPsb" in onclick_attribute) and ('N' in onclick_attribute):
                        print(f'시험보기 버튼을 찾았습니다: {button}')
                        button.click()
                        time.sleep(0.5)
                        self.click('//*[@id="myclass-edu-attn-window"]/div[1]/label/span')
                        self.click('//*[@id="myclass-edu-attn-window"]/div[2]/div/button[2]')
                        time.sleep(0.5)
                        self.log_network_traffic()
        except Exception as e:
            print(e)

    def log_network_traffic(self):
        """네트워크 요청 및 응답 로그를 출력"""
        # 성능 로그 (performance) 가져오기
        logs = self.driver.get_log("performance")
        for entry in logs:
            message = json.loads(entry['message'])
            if 'message' in message and 'Network.responseReceived' in message['message']['method']:
                response = message['message']['params']['response']
                if 'insert' in response.get('url', ''):  # 특정 URL에 대한 응답 처리
                    print("Insert 데이터 찾음:")
                    print(json.dumps(response, indent=2))

    def get_network_answer(self):
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

    def click(self, x_path=''):
        click_element = self.driver.find_element(By.XPATH, x_path)
        self.driver.execute_script("arguments[0].scrollIntoView();", click_element)
        click_element.click()
        time.sleep(0.5)

    def input(self, x_path='', input=''):
        click_element = self.driver.find_element(By.XPATH, x_path)
        click_element.click()
        click_element.send_keys(input)
        time.sleep(0.5)

    def quit(self):
        time.sleep(5)
        self.driver.quit()


if __name__ == "__main__":
    SE = SafeEdu()
    SE.log_in()
    SE.enter_classroom()
    SE.find_next_study_button()
    SE.wait_for_progress_and_click()

    time.sleep(30)
    SE.quit()
