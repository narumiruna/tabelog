from typing import Final

from dotenv import find_dotenv
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

PROMPT: Final[str] = """
あなたは食べログの検索用に最適化された日本語の自然言語処理モデルです。以下のユーザー入力から、食べログで検索に使う「area（エリア）」と「keyword（キーワード）」を抽出してください。キーは "area" と "keyword"、値は必ず日本語にしてください。エリアは地名（例: 東京、新宿、渋谷など）を簡潔に、キーワードは料理名やジャンル（例: 寿喜焼き、ラーメン）を返してください。値が特定できない場合は空文字 ("") を返してください。

ユーザー入力:
{user_input}
""".strip()


class SearchRequest(BaseModel):
    area: str
    keyword: str


def parse_user_input(user_input: str) -> SearchRequest:
    load_dotenv(find_dotenv())

    client = OpenAI()
    response = client.responses.parse(
        model="gpt-4.1",
        input=PROMPT.format(user_input=user_input),
        text_format=SearchRequest,
    )

    if response.output_parsed is None:
        raise ValueError("Failed to parse user input")

    return response.output_parsed
