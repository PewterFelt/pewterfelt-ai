import urllib.parse
from typing import cast

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


def get_favicon(soup: BeautifulSoup, url: str):
    favicon = None
    icon_link = cast(
        Tag, soup.find("link", rel=lambda rel: bool(rel and "icon" in rel.lower()))
    )

    if icon_link and icon_link.get("href"):
        favicon = urllib.parse.urljoin(url, cast(NavigableString, icon_link["href"]))
    else:
        parsed_url = urllib.parse.urlparse(url)
        favicon = f"{parsed_url.scheme}://{parsed_url.netloc}/favicon.ico"

    return favicon


def get_meta_image(soup: BeautifulSoup, url: str):
    meta_image = None
    og_image_tag = cast(Tag, soup.find("meta", property="og:image"))

    if og_image_tag and og_image_tag.get("content"):
        meta_image = urllib.parse.urljoin(
            url, cast(NavigableString, og_image_tag.get("content"))
        )

    return meta_image


def parse(html: str, url: str):
    try:
        soup = BeautifulSoup(html, "html.parser")

        favicon = get_favicon(soup, url)
        meta_image = get_meta_image(soup, url)

        return {"favicon": favicon, "meta_image": meta_image}, None
    except Exception as e:
        return None, {"status": 500, "message": str(e)}
