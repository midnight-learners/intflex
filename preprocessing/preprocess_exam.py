from docx import Document
import re
import os
import json


def process_raw_text_to_dict(raw_text):
    # 使用正则表达式提取题目信息
    match = re.match(r'(\d+)、(.*?)<(\w+)>(.*?)\n', raw_text)
    if match:
        question_id = int(match.group(1))
        question_text = match.group(2) + "<>" + match.group(4)
        answers = match.group(3)

        # 使用正则表达式提取选项信息
        # choices_match = re.findall(r'([A-D])、(.*?)\n', input_string)
        choices_match = re.findall(r'([A-D])、(.*?)(?=[A-D]、|\n|$)', raw_text)
        choices = {choice[0]: choice[1] for choice in choices_match}

        # 构建字典
        result = {
            'id': question_id,
            # 'question': question_text.replace('<>', '<{}>'.format(answer)),
            'question': question_text,
            'choices': choices,
            'answer': [answer for answer in answers]
        }
        return result
    else:
        return None


def preprocess_exam_paper(directory_path: str = './document_exam'):
    file_names = [file_name for file_name in os.listdir(directory_path) if file_name.endswith(".docx")]
    output_directory_path = './document_exam_json'
    for file_name in file_names:
        print(f"processing {file_name}...")
        doc = Document(f"{directory_path}/{file_name}")
        output_file_name = file_name.split(".")[0]

        text = "".join([paragraph.text + "\n" for paragraph in doc.paragraphs]).replace(" ", "")
        # 替换括号
        text = text.replace("(", "<").replace(")", ">").replace("（", "<").replace("）", ">")

        # 使用正则表达式分割文本成题目段落
        pattern = r'\d+、.*?(?=\d+、|\Z)'
        questions = re.findall(pattern, text, re.DOTALL)

        # 打印分段后的题目段落
        json_data = []
        for index, question in enumerate(questions, start=1):
            print(f'题目 {index}:')
            json_question = process_raw_text_to_dict(question)
            json_data.append(json_question)
            print(json_question)
            print('-' * 50)

        with open(f"{output_directory_path}/{output_file_name}.json", "w") as json_file:
            json.dump(json_data, json_file, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # # 测试示例
    # input_string1 = '1、《中华人民共和国职业病防治法》于<B>正式实施。\nA、2001年10月27日B、2002年5月1日C、2002年1月1日D、2002年7月1日\n'
    # input_string2 = '2、职业病指<B>\nA、劳动者在工作中所患的疾病\nB、用人单位的劳动者在职业活动中，因接触粉尘、放射性物质和其他有毒、有害物质等因素而引起的疾病\nC、工人在劳动过程中因接触粉尘、有毒、有害物质而引起的疾病\nD、工人在职业活动中引起的疾病\n'
    #
    # result1 = process_raw_text_to_dict(input_string1)
    # result2 = process_raw_text_to_dict(input_string2)
    #
    # print(result1)
    # print(result2)
    preprocess_exam_paper()
