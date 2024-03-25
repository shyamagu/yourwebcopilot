import os
from dotenv import load_dotenv
load_dotenv()

AOAI_API_KEY = os.getenv("AOAI_API_KEY")
AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")
AOAI_MODEL = os.getenv("AOAI_MODEL")

from logger import logger

from openai import AzureOpenAI

def call_chatgpt (messages,temperature=0):

    client = AzureOpenAI(
        azure_endpoint = AOAI_ENDPOINT, 
        api_key=AOAI_API_KEY,  
        api_version="2023-12-01-preview",
        timeout=60,
        max_retries=3,
    )

    response = client.chat.completions.create(
    model=AOAI_MODEL, # model = "deployment_name".
    messages=messages,
    temperature=temperature,
    )

    return response.choices[0].message.content


def call_chatgpt_w_stream (messages,temperature=0):

    client = AzureOpenAI(
        azure_endpoint = AOAI_ENDPOINT, 
        api_key=AOAI_API_KEY,  
        api_version="2023-12-01-preview",
        timeout=60,
        max_retries=3,
    )

    stream = client.chat.completions.create(
        model=AOAI_MODEL,
        messages=messages,
        temperature=temperature,
        stream = True,
    )

    return stream
