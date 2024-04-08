import requests
from transformers import AutoTokenizer
from config import *
import logging

user_data = {}
user_collection = {}


def count_tokens(prompt):
    tokenizer = AutoTokenizer.from_pretrained("IlyaGusev/saiga_mistral_7b")
    return len(tokenizer.encode(prompt))


def create_system_prompt(data, user_id):
    prompt = SYSTEM_PROMPT
    prompt += (f"\nНапиши рекомендацию по подарку на праздник {data[user_id]['holiday']} "
               f"Получателю {data[user_id]['recipient']}. "
               "Рекомендация должна быть короткой, 10-15 предложений.\n")
    if not data[user_id]['age'] is None:
        prompt += f"Так же пользователь попросил учесть возраст получателя - {data[user_id]['age']} "
    prompt += 'Не пиши никакие подсказки пользователю, что делать дальше. Он сам знает'
    return prompt


def ask_gpt(collection, mode='continue'):
    data = {
        "messages": [],
        "temperature": 0.6,
        "max_tokens": MAX_TOKENS,
    }

    for row in collection:
        content = row['content']
        # Добавляем дополнительный текст к сообщению пользователя в зависимости от режима
        data["messages"].append(
                {
                    "role": row["role"],
                    "content": content
                }
            )
    try:
        response = requests.post(GPT_LOCAL_URL, headers=HEADERS, json=data)
        if response.status_code != 200:
            logging.debug(f"Response {response.json()} Status code:{response.status_code} Message {response.text}")
            result = f"Status code {response.status_code}. Подробности см. в журнале."
            return result
        result = response.json()['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        result = "Произошла непредвиденная ошибка. Подробности см. в журнале."

    return result
