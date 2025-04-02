from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel

from app.crawler import crawl
from app.parser import parse
from app.security import verify_token
from app.tagger import tag

load_dotenv()  # pyright: ignore[reportUnusedCallResult]


app = FastAPI(dependencies=[Depends(verify_token)])


class UrlRequest(BaseModel):
    url: str
    tags: list[str]


@app.post("/api/tag")
async def tag_url(request: UrlRequest, response: Response):
    result, crawl_error = await crawl(request.url)
    if not result or not result.markdown:
        if crawl_error:
            response.status_code = int(crawl_error["status"] or 500)
            return {"error": crawl_error["message"]}
        response.status_code = 500
        return {"error": "Failed to crawl URL"}

    tags, tag_error = tag(result.markdown, request.tags)
    if not tags:
        if tag_error:
            response.status_code = int(tag_error["status"])
            return {"error": tag_error["message"]}
        response.status_code = 500
        return {"error": "Failed to tag content"}

    metadata, parse_error = parse(result.html, request.url)
    if not metadata:
        if parse_error:
            response.status_code = int(parse_error["status"])
            return {"error": parse_error["message"]}
        response.status_code = 500
        return {"error": "Failed to parse metadata"}

    response_data = {"tags": tags, "metadata": metadata}

    return response_data


@app.api_route("/api/ping", methods=["GET", "HEAD"])
async def ping():
    return {"message": "healthy"}
