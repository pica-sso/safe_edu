import json


class GetAnswer:
    def __init__(self):
        self.answer_list = []

    def run(self):
        self.insert_response()
        # self.clear()

    def insert_response(self):
        with open("response.txt", 'r', encoding='utf-8') as file:
            response = file.read()

        try:
            # JSON 응답을 파싱합니다.
            data = json.loads(response)

            # 답 리스트
            self.answer_list = []

            for item in data['data']['items']:
                for exam in item['examList']:
                    if exam['ANSR_YN'] == 'Y':
                        self.answer_list.append(exam['EXAM_NUM']-1)
            # print(self.answer_list)
        except Exception as ex:
            print("response.txt에 알맞게 복사해 넣었는지 확인하고 저장한뒤 y를 눌러주세요")
            y = input()
            self.insert_response()

    def clear(self):
        with open("response.txt", 'w', encoding='utf-8') as file:
            file.write('')


if __name__ == "__main__":
    answer = GetAnswer()
    answer.run()
    print(answer.answer_list)
