from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from app.crawler import crawl
from app.parser import parse
from app.tagger import tag

load_dotenv()  # pyright: ignore[reportUnusedCallResult]

app = FastAPI()


class UrlRequest(BaseModel):
    url: str


@app.post("/api/tag")
async def tag_url(request: UrlRequest):
    result, crawl_error = await crawl(request.url)
    if not result or not result.markdown:
        if crawl_error:
            return {"error": crawl_error["message"]}, crawl_error["status"]
        return {"error": "Failed to crawl URL"}, 500

    tags, tag_error = tag(result.markdown)
    if not tags:
        if tag_error:
            return {"error": tag_error["message"]}, tag_error["status"]
        return {"error": "Failed to tag content"}, 500

    metadata, parse_error = parse(result.html, request.url)
    if not metadata:
        if parse_error:
            return {"error": parse_error["message"]}, parse_error["status"]
        return {"error": "Failed to parse metadata"}, 500

    return {"tags": tags, "metadata": metadata}
