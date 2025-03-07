from fastapi import FastAPI
from pydantic import BaseModel

from app.crawler import crawl
from app.parser import parse

app = FastAPI()


class UrlRequest(BaseModel):
    url: str


@app.post("/api/tag")
async def tag_url(request: UrlRequest):
    result, error = await crawl(request.url)

    if not result:
        if error:
            return {"error": error["message"]}, error["status"]
        return {"error": "Failed to crawl URL"}, 500

    metadata = parse(result.html, request.url)

    return {"markdown": result.markdown, "metadata": metadata}
