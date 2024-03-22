import requests
import lxml.html
import readability
import re
from logger import logger

def analyze_html(url):

    #urlのHTMLを取得する
    response = requests.get(url,timeout=10)

    response.encoding = response.apparent_encoding

    html = response.text

    #HTMLから本文だけを抽出する
    document = readability.Document(html)
    content_html = document.summary()

    content_text = lxml.html.fromstring(content_html).text_content()

    #content_text から2文字以上続く空白や改行を1文字にする 
    content_text = re.sub(r"\s+", " ", content_text) 
    content_text = re.sub(r"\n+", "\n", content_text) 

    short_title = document.short_title()
    
    return short_title,content_text
