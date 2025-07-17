import json
import random
import time
import logging
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://dolis.gaia.domains"
MODEL = "qwen2-0.5b-instruct"
MAX_RETRIES = 100
RETRY_DELAY = 5
QUESTION_DELAY = 1

def load_questions(file_path="questions.json"):
    """
    Загружает вопросы из файла questions.json.
    """
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
        return data["questions"]
    except FileNotFoundError:
        logging.error(f"File {file_path} not found.")
        raise
    except json.JSONDecodeError:
        logging.error(f"Error decoding JSON from {file_path}.")
        raise

def chat_with_ai(api_key: str, question: str):
    """
    Отправка вопроса в API и получение ответа.
    """
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    messages = [{"role": "user", "content": question}]
    data = {"model": MODEL, "messages": messages, "temperature": 0.7}

    for attempt in range(MAX_RETRIES):
        try:
            logging.info(f"Attempt {attempt+1} for question: {question[:50]}...")
            response = requests.post(f"{BASE_URL}/v1/chat/completions", headers=headers, json=data, timeout=30)

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            logging.warning(f"API Error ({response.status_code}): {response.text}")
            time.sleep(RETRY_DELAY)

        except Exception as e:
            logging.error(f"Request failed: {str(e)}")
            time.sleep(RETRY_DELAY)

    raise Exception("Max retries exceeded")

def run_bot(api_key: str, questions):
    """
    Основной процесс для запуска бота, включая обработку вопросов.
    """
    random.shuffle(questions)
    logging.info(f"Starting chatbot with {len(questions)} questions in random order")

    for i, question in enumerate(questions, 1):
        logging.info(f"\nProcessing question {i}/{len(questions)}")
        logging.info(f"Question: {question}")

        start_time = time.time()
        try:
            response = chat_with_ai(api_key, question)
            elapsed = time.time() - start_time

            # Печать полного ответа
            print(f"Answer to '{question[:50]}...':\n{response}")

            logging.info(f"Received full response in {elapsed:.2f}s")
            logging.info(f"Response length: {len(response)} characters")

            # Пауза перед следующим вопросом
            time.sleep(QUESTION_DELAY)

        except Exception as e:
            logging.error(f"Failed to process question: {str(e)}")
            continue

def main():
    """
    Основная точка входа в программу.
    """
    print("Title: GaiaAI Chatbot")
    print("Twitter: https://x.com/0xMoei")
    api_key = input("Enter your API key: ")
    questions = load_questions()
    run_bot(api_key, questions)

if __name__ == "__main__":
    main()
    