# SafeEdu 자동화 프로그램

교육 플랫폼에서 교육을 자동으로 듣고 시험을 자동으로 보는 프로그램입니다.
Selenium WebDriver와 Chrome을 사용하여 브라우저를 자동화하며,
로그인, 학습, 시험 제출의 과정을 자동으로 처리합니다.

## 기능

- **자동 로그인**: `.env` 파일에 저장된 사용자 정보를 이용하여 자동으로 로그인합니다.
- **교육 모듈 자동화**: 교육 콘텐츠를 자동으로 탐색하고 학습을 시작합니다.
- **시험 자동 제출**: 교육이 완료되면 자동으로 답안을 선택하여 시험을 제출합니다.
- **에러 처리**: 실행 중 발생할 수 있는 오류를 처리하고 로그를 기록하여 문제를 추적할 수 있습니다.
- **헤드리스 모드**: UI 없이 브라우저를 백그라운드에서 실행할 수 있습니다.
- **화면 줌 조정**: 웹페이지의 줌 레벨을 조정하여 원활한 인터랙션을 제공합니다.

## 요구 사항

- Python 3.11.2
- Selenium (`pip install selenium`)
- ChromeDriver (구글 크롬 버전에 맞는 드라이버 다운로드)
- dotenv (`pip install python-dotenv`)

## 설치 방법

1. **필요한 패키지 설치**:  
   Python 3.11.2로 가상환경을 생성하고 requirements를 설치합니다.

   ```bash
   pip install -r requirements.txt
   ```

2. **ChromeDriver 다운로드**:
   
   ChromeDriver 사이트에서 본인의 크롬 버전에 맞는 드라이버를 다운로드하고,
   프로젝트 루트에 chromedriver-win64 폴더를 만들어 드라이버 파일을 넣습니다.

3. **`.env` 파일 설정**:  
   프로젝트 루트에 `.env` 파일을 생성하고, 아래와 같이 사이트와 로그인 정보를 입력합니다:

   ```ini
   USERID=사용자아이디
   PASSWORD=비밀번호
   SITEURL=사이트 url
   BUSINESS_NUM=사업자번호
   CHROMEDRIVER_PATH=chromedriver 실행 파일 위치
   ```

## 사용 방법

1. 레포지토리를 클론합니다:

   ```bash
   git clone https://github.com/pica-sso/safe_edu.git
   cd SafeEdu

2. 스크립트를 실행합니다.

    ```bash
    python safe_edu.py
    ```
   
실행 시, 프로그램은 다음과 같은 작업을 자동으로 처리합니다:
- 웹사이트에 로그인하고, 교육 콘텐츠를 탐색합니다.
- 교육이 완료되면 자동으로 시험을 제출합니다.
- 시험 제출 후 알림 팝업을 자동으로 처리합니다.


### download link:
- BrowserMob Proxy : https://github.com/lightbody/browsermob-proxy/releases