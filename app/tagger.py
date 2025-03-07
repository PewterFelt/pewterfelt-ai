import requests
import json

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

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": "Bearer <OPENROUTER_API_KEY>",
        "HTTP-Referer": "<YOUR_SITE_URL>",  # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>",  # Optional. Site title for rankings on openrouter.ai.
    },
    data=json.dumps(
        {
            "model": "openai/gpt-4o",  # Optional
            "messages": [{"role": "user", "content": "What is the meaning of life?"}],
        }
    ),
)
