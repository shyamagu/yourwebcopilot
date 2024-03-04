import os
from dotenv import load_dotenv
load_dotenv()

BING_API_KEY = os.getenv("BING_API_KEY")

import requests
from requests.exceptions import Timeout

from logger import logger

def call_bingapi (url,query,option):

    bingurl = url+query+option

    logger.debug(bingurl)

    #bingurlにHeaderつきのGETリクエストを送り結果を取得する
    try:
        result = requests.get(bingurl,headers={'Ocp-Apim-Subscription-Key': BING_API_KEY},timeout=5)
    except Timeout:
        return []

    result.raise_for_status()
    #result からJSONを取得する
    result = result.json()

    return result["webPages"]["value"]
