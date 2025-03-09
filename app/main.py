import json
import os
from contextlib import asynccontextmanager
from datetime import timedelta
from typing import cast

from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from glide import (
    ExpirySet,
    ExpiryType,
    GlideClient,
    GlideClientConfiguration,
    NodeAddress,
)
from pydantic import BaseModel

from app.crawler import crawl
from app.parser import parse
from app.security import verify_token
from app.tagger import tag

load_dotenv()  # pyright: ignore[reportUnusedCallResult]


@asynccontextmanager
async def lifespan(app: FastAPI):
    valkey_host = os.getenv("VALKEY_HOST", "localhost")
    valkey_port = int(os.getenv("VALKEY_PORT", 6379))
    addresses = [NodeAddress(host=valkey_host, port=valkey_port)]

    client_config = GlideClientConfiguration(addresses)
    if os.getenv("VALKEY_TLS_ENABLED", "false").lower() == "true":
        client_config.use_tls = True

    app.state.valkey = await GlideClient.create(client_config)
    yield

    await app.state.valkey.close()


app = FastAPI(lifespan=lifespan, dependencies=[Depends(verify_token)])


class UrlRequest(BaseModel):
    url: str


@app.post("/api/tag")
async def tag_url(request: UrlRequest):
    valkey = cast(GlideClient, app.state.valkey)

    cached = await valkey.get(request.url)
    if cached:
        return json.loads(cached)  # pyright: ignore[reportAny]

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

    response_data = {"tags": tags, "metadata": metadata}

    await valkey.set(
        request.url,
        json.dumps(response_data),
        expiry=ExpirySet(expiry_type=ExpiryType.MILLSEC, value=2592000),
    )  # pyright: ignore[reportUnusedCallResult]

    return response_data
