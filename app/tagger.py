import os
from typing import cast

import requests
from crawl4ai.models import StringCompatibleMarkdown

PROMPT_TEMPLATE = """
{content}

* * *

Analyze the content and generate up to five relevant tags that best represent its core topics. Follow these guidelines:

1. Prioritize specific terms over general ones
2. Use lower case with spaces (e.g., "machine learning")
3. Use uppercase without dots for acronyms (e.g., "UI", "CLI", "AI", "ETF")
4. Have no spaces around the commas, only for compound meanings (e.g., "machine learning", "web development", "climate change")
4. Maximum 5 tags, minimum 2

* * *

Examples:
- Neovim configuration guide → `CLI,tech,lua,neovim,IDE`
- Python web development tutorial → `python,web development,backend,programming,tech`
- Healthy meal recipe → `cooking,recipe,nutrition,healthy eating`
- React performance optimization → `web development,react,javascript`
- Climate change analysis → `environment,science,climate change,sustainability`
- Personal finance tips → `finance,personal finance,money management,investing`
- Machine learning fundamentals → `AI,machine learning,data science,mathematics`
- Travel guide to Japan → `travel,japan,culture,tourism`

* * *

Return only a comma-separated list of tags with no additional formatting or explanation.
"""


def tag(content: StringCompatibleMarkdown):
    try:
        prompt = PROMPT_TEMPLATE.format(content=content)

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                # "HTTP-Referer": os.getenv("SITE_URL", ""),
                # "X-Title": os.getenv("SITE_NAME", ""),
            },
            json={
                "model": "meta-llama/llama-3.3-70b-instruct",
                "messages": [{"role": "user", "content": prompt}],
            },
        )

        response.raise_for_status()

        if "error" in response.json():
            import json

            error_json = response.json()["error"]
            raw_message = error_json["metadata"]["raw"]

            try:
                parsed_message = json.loads(raw_message)
            except json.JSONDecodeError:
                parsed_message = raw_message

            return None, {
                "status": error_json["code"],
                "message": parsed_message,
            }

        tags_str = cast(
            str, response.json()["choices"][0]["message"]["content"]
        ).strip()

        return [t.strip() for t in tags_str.split(",")], None

    except requests.HTTPError as e:
        return None, {"status": e.response.status_code, "message": e.response.text}
