import openai
import json
import os
from dotenv import load_dotenv
from tqdm import tqdm


def parse_raw_questions_to_json(raw_questions: str) -> list[dict]:
    """
    Parse ChatGPT generated string content, and convert each generated question --to--> json format
    :param raw_questions: string of ChatGPT response
    :return: list of question in json format
    """
    processed_question = []
    for raw_question in raw_questions.split('<DIVIDED>'):
        raw_question = raw_question.strip().split('\n')
        json_question = {}
        for section in raw_question:
            if section.startswith("question"):
                question_content = section.split("question:")[1].strip()
                json_question["question"] = question_content

            elif section.startswith("options"):
                json_options = {}
                for option in section.split("options:")[1].split("|"):
                    option_tag = option.split(":")[0].strip()
                    option_content = option.split(":")[1].strip()
                    json_options[option_tag] = option_content
                json_question["options"] = json_options

            elif section.startswith("answer"):
                answer_content = section.split("answer:")[1].strip()
                json_question["answer"] = answer_content

        processed_question.append(json_question)
    return processed_question


def split_text(text: str, split_length: int = 1000) -> list[str]:
    split_text_list = []
    text_length = len(text)
    for i in range(0, text_length, split_length):
        if i + 2 * split_length >= text_length - 1:
            split_text_list.append(text[i:])
            break
        else:
            split_text_list.append(text[i:i + split_length])

    return split_text_list


def generate_question(article: str) -> list[dict]:
    """
    Generate question based on article
    """

    """Extract key knowledge points"""
    prompt_1 = """
    You have been assigned the responsibility of overseeing staff training. \
    There is a company article available for your reference. \
    Your objective is to analyze the 5 key knowledge points mentioned in the article \
    that you believe are crucial for new employees, \
    and provide a comprehensive summary for each point using elaborate sentences. \
    Please label each knowledge point with a number and respond in Chinese.

    Article: ```{article}```
    """.format(article=article)

    response_gpt_1 = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt_1,
        temperature=0.7,
        max_tokens=2048,
        n=1,
    )
    extracted_knowledge_points = response_gpt_1.choices[0].text
    print(f"1st respond successfully...")

    """Generate question base on the knowledge point"""
    prompt_2 = """
    You are the person in charge of employee orientation, and you have a list of knowledge points. \
    Your task is to generate a multiple-choice question for each knowledge point to see \
    how well the employee has mastered the knowledge point. \
    Each multiple-choice question has 1 correct option and 3 interference options(must ensure the interference option is erroneous). \
    Please output each question in key: value format, make sure value content is Chinese and key name is English. 

    Output Example:
    ```
    question: <your generated question>
    options: A: <Option A content> | B: <Option B content> | C: <Option C content> | D: <Option D content>\n
    answer: <The correct option of your generated question>
    <DIVIDED>
    ```

    Knowledge points: ```{knowledge_points}```
    """.format(knowledge_points=extracted_knowledge_points)

    response_gpt_2 = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=prompt_2,
        temperature=0.8,
        max_tokens=2048,
        n=1,
    )
    raw_questions = response_gpt_2.choices[0].text
    print(f"2nd respond successfully...")
    print(raw_questions)

    return parse_raw_questions_to_json(raw_questions)


if __name__ == "__main__":
    load_dotenv()
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    openai.proxy = "http://127.0.0.1:7890"

    with open("../document_txt/人力资源部/ZC-S-H-002RBA管理手册（A1）.txt", "r") as f:
        txt = f.read()

    text_list = split_text(txt)

    json_question_list = []
    for text in tqdm(text_list[:2], desc="Processing Texts"):  # 添加tqdm进度条
        json_question_list += generate_question(article=text)

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(json_question_list, f, ensure_ascii=False, indent=4)
