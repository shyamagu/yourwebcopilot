from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import tiktoken

def encode_token(text):
    encoding_4 = tiktoken.encoding_for_model("gpt-4")
    encoding = tiktoken.get_encoding(encoding_4.name)
    encoded = encoding.encode(text)
    return encoded

def calc_token(text):
    encoded = encode_token(text)
    return len(encoded)

import requests
import json

from common.call_chatgpt import call_chatgpt, call_chatgpt_w_stream

from common.call_chatgpt import call_chatgpt, call_chatgpt_w_stream
from common.call_bingapi import call_bingapi
from common.analyze_html import analyze_html

from fastapi.responses import StreamingResponse

from logger import logger

router = APIRouter()

class Message(BaseModel):
    role: str
    content: str

class ReceiveData(BaseModel):
    content: str
    searchEnglish: bool
    sitelist: List[str]

@router.post("/yourwebcopilot/getbingresult")
def mslcopilot_part1(message: ReceiveData):

    content = message.content
    searchEnglish = message.searchEnglish
    siteoption = "%20OR".join(["%20site:" + site for site in message.sitelist])

    if searchEnglish:
        system_prompt ="""You are a top-tier information concierge. Based on user input, return the necessary Bing search queries in the following format in English.
If the user explicitly specifies search keywords, use those as the search query. 
**No need for additional explanations or descriptions. Only answer with the array string format.**

Output format:
["query1","query2","query3"]

Sample)
Input: "What is Azure?"
Output: ["Azure","Overview"]

Input: "I want to know about typical problems with ACA"
Output: ["Azure Container Apps","Troubleshooting"]

Input: "Summarize the search results for 'GPT-4V, schematic diagram'"
Output: ["GPT-4V","schematic diagram"]
"""
    else:
        system_prompt ="""あなたはMSLearnの情報コンシェルジュです。ユーザの入力からMSLearnで必要となる検索クエリを以下のフォーマットで返します。
もしユーザから検索キーワードの明示的な指定があればそれを検索クエリとしてください。
**補足や説明は不要です。出力フォーマットの配列文字列のみ回答してください。**

出力フォーマット:
["query1","query2","query3"]

サンプル)
入力:「Azureとは?」
出力:["Azure","概要"]

入力:「ACAの代表的な問題について知りたい」
出力:["Azure Container Apps","トラブルシューティング"]

入力:「"GPT-4V,構成図"で検索した結果を要約して」
出力: ["GPT-4V","構成図"]
"""

    messages_for_query = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=content)
    ]

    # ChatGPTを呼び出す
    answer_query = call_chatgpt([m.dict() for m in messages_for_query])
    logger.debug(answer_query)
    
    try:
        bingsearchurl = "https://api.bing.microsoft.com/v7.0/search?q="
        querystring = "%20".join(eval(answer_query))
    except Exception as e:
        data = {
            "message": answer_query,
            "query":"",
            "searchResult":[],
        }
        return JSONResponse(content=data)

    if siteoption:
        querystring += siteoption
    if searchEnglish:
        querystring += "%20language:=en"
    option = "&count=10&offset=0"
    #"&count=5&offset=0&mkt=ja-JP"
 
    try:
        bingResult = call_bingapi(bingsearchurl,querystring,option)
    except Exception as e:
        data = {
            "message": "Bing検索に失敗しました。",
            "query":"",
            "searchResult":[],
        }
        return JSONResponse(content=data)

    # bingResult配列からname, url, snippetのみを残した配列を作成する
    filtered_bingResult = []
    for result in bingResult:
        filtered_result = {
            "name": result["name"],
            "url": result["url"],
            "snippet": result["snippet"]
        }
        filtered_bingResult.append(filtered_result)

    data = {
        "message": content,
        "query":answer_query,
        "searchResult":filtered_bingResult,
    }
    # JSONResponseに辞書型のデータを渡して返す
    return JSONResponse(content=data)

class AdviceRequest(BaseModel):
    content: str
    url: str
    name: str
    query: str
    searchEnglish: bool
    forceExecute: bool

def chatgpt_streamer(response):
    for chunk in response:
        if chunk is not None and chunk.choices:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

def chatgpt_streamer_dummy(response):
    yield response

@router.post("/yourwebcopilot/getadvicews")
def getadvice(request: AdviceRequest):

    message = request.content
    url = request.url
    query = request.query
    searchEnglish = request.searchEnglish
    forceExecute = request.forceExecute

    try:
        short_title, content_text = analyze_html(url)
        token_num = calc_token(content_text)

    except Exception as e:
        logger.error(e)
        advice = "ページ情報の解析に失敗しました"
        return StreamingResponse(
            chatgpt_streamer_dummy(advice), media_type="text/event-stream"
        )

    if searchEnglish:
        system_prompt =f"""You are a top-tier information concierge well-versed in technology.
Respond to user questions using only the information from the page provided, aiming for concise and to-the-point answers in Japanese.
Additionally, encourage users to refer to the page information for more details.
If the user's question is not covered by the page information, simply respond 'NOT FOUND', without providing any further explanation.
**Responses will be written in Japanese.**

Example when no question was included:
User: Tell me about the pricing of Azure.
You: NOT FOUND

### Page Information
Search Query: {query}

Title: {short_title}

Content:
{content_text}
"""
    else:
        system_prompt =f"""あなたはテクノロジーに精通した一流の情報コンシェルジュです。
ユーザの質問について、以下のページ情報のみを利用して、なるべく簡潔で要点をまとめた回答を返します。
その上で、詳細な内容についてはページ情報を参照するように促してください。
もしページ情報にユーザの質問内容が含まれない場合は、「NOT FOUND」とのみ回答してください。説明や補足は不要です。

質問が含まれなかった時の例:
ユーザ:Azureの料金について教えて
あなた:NOT FOUND

###ページ情報
検索クエリ: {query}

Title: {short_title}

Content : 
{content_text}
"""
            
    messages_for_advice = [
        Message(role="system", content=system_prompt),
        Message(role="user", content=message)
    ]

    if token_num <= 100 and not forceExecute:
        advice = "!ページ情報のトークン数が規定値(100)に満たないため、要約処理は行いません。\nページ情報が取得できていない可能性があります。リンク先を確認ください。"
        return StreamingResponse(
            chatgpt_streamer_dummy(advice), media_type="text/event-stream"
        )

    if token_num < 10000 or forceExecute:
        advice = call_chatgpt_w_stream([m.dict() for m in messages_for_advice])

        return StreamingResponse(
            chatgpt_streamer(advice), media_type="text/event-stream"
        )

    else:
        advice = f"!ページ情報のトークン数が規定値を超えている(token:{token_num} > 10000)ため要約処理を見送りました。\n参考リンクを直接ご参照ください。"

        return StreamingResponse(
            chatgpt_streamer_dummy(advice), media_type="text/event-stream"
        )

