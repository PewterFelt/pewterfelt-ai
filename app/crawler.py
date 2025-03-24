from typing import cast

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    CrawlResult,
)


async def crawl(url: str):
    browser_conf = BrowserConfig(headless=True, verbose=True)
    config = CrawlerRunConfig(
        # cache_mode=CacheMode.BYPASS,
        cache_mode=CacheMode.ENABLED,
        word_count_threshold=10,
        excluded_tags=["form", "header", "footer", "nav"],
        exclude_external_links=True,
        remove_overlay_elements=True,
        process_iframes=True,
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = cast(
            CrawlResult,
            cast(
                object,
                await crawler.arun(url=url, config=config),  # pyright: ignore[reportUnknownMemberType]
            ),
        )
        if not result.success:
            return None, {"status": result.status_code, "message": result.error_message}

        # Process links
        # for link in result.links["internal"]:
        #     print(f"Internal link: {link['href']}")

        return result, None
