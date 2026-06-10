import json
import logging
from datetime import date
from typing import Any

from src.config import settings, SEARCH_RESULTS_PER_QUERY

logger = logging.getLogger(__name__)

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_market",
            "description": (
                "搜索中国电商市场数据，获取热销产品、销量趋势、品类整体动态。"
                "适合用于品类整体研究。搜索覆盖淘宝、1688、百度、小红书。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "中文搜索词，例如：'淘宝2024卷纸热销款式推荐'、"
                            "'家用洗衣液市场趋势爆款'、'湿巾品牌消费者推荐'"
                        ),
                    },
                    "focus": {
                        "type": "string",
                        "enum": ["trending", "competition", "pricing", "consumer_reviews"],
                        "description": (
                            "搜索侧重点："
                            "trending=热销趋势, competition=竞争格局, "
                            "pricing=价格区间, consumer_reviews=消费者评价"
                        ),
                    },
                },
                "required": ["query", "focus"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_product_detail",
            "description": (
                "对特定产品进行深度研究，获取1688供货价、竞争对手数量、"
                "消费者需求和差异化机会。在识别候选产品后使用此工具。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "产品中文名称，例如：'无荧光剂抽纸'、'浓缩洗衣液'",
                    },
                    "aspect": {
                        "type": "string",
                        "enum": [
                            "supplier_pricing",
                            "competitor_analysis",
                            "consumer_demand",
                            "differentiation",
                        ],
                        "description": (
                            "研究维度："
                            "supplier_pricing=1688供货价格, competitor_analysis=竞争对手分析, "
                            "consumer_demand=消费者需求, differentiation=差异化机会"
                        ),
                    },
                },
                "required": ["product_name", "aspect"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_current_date",
            "description": "返回今天的日期，用于季节性分析和时效性判断。",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]

_FOCUS_TO_DOMAINS = {
    "trending": ["taobao.com", "baidu.com", "xiaohongshu.com", "weibo.com"],
    "competition": ["taobao.com", "tmall.com", "jd.com"],
    "pricing": ["1688.com", "taobao.com", "pinduoduo.com"],
    "consumer_reviews": ["xiaohongshu.com", "zhihu.com", "baidu.com"],
}

_ASPECT_TO_QUERY = {
    "supplier_pricing": "1688 {product} 供应商 批发价格 进货",
    "competitor_analysis": "淘宝 {product} 竞争对手 销量排名 卖家数量",
    "consumer_demand": "{product} 消费者需求 热度 购买理由 评价",
    "differentiation": "{product} 差异化卖点 创新 小众 特色",
}

_FOCUS_TO_SITE = {
    "trending": "site:taobao.com OR site:baidu.com OR site:xiaohongshu.com",
    "competition": "site:taobao.com OR site:tmall.com OR site:jd.com",
    "pricing": "site:1688.com OR site:taobao.com OR site:pinduoduo.com",
    "consumer_reviews": "site:xiaohongshu.com OR site:zhihu.com OR site:baidu.com",
}

_ASPECT_TO_SITE = {
    "supplier_pricing": "site:1688.com OR site:taobao.com",
    "competitor_analysis": "site:taobao.com OR site:tmall.com OR site:jd.com",
    "consumer_demand": "site:baidu.com OR site:xiaohongshu.com OR site:zhihu.com",
    "differentiation": "site:xiaohongshu.com OR site:zhihu.com OR site:baidu.com",
}


def _do_search(query: str) -> list[dict]:
    """Route to Serper if key is configured, otherwise fall back to Baidu scraping."""
    if settings.serper_api_key and not settings.serper_api_key.startswith("your_"):
        return _serper_search(query)
    return _baidu_search(query)


def _serper_search(query: str) -> list[dict]:
    import requests as req
    resp = req.post(
        "https://google.serper.dev/search",
        headers={"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"},
        json={"q": query, "gl": "cn", "hl": "zh-cn", "num": SEARCH_RESULTS_PER_QUERY},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    return [
        {
            "title": r.get("title", ""),
            "url": r.get("link", ""),
            "snippet": r.get("snippet", "")[:400],
        }
        for r in data.get("organic", [])[:SEARCH_RESULTS_PER_QUERY]
    ]


def _baidu_search(query: str) -> list[dict]:
    """Scrape Baidu search results. Works on any machine with normal internet access."""
    import requests as req
    from bs4 import BeautifulSoup

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    params = {"wd": query, "rn": SEARCH_RESULTS_PER_QUERY, "ie": "utf-8"}
    resp = req.get(
        "https://www.baidu.com/s", params=params, headers=headers, timeout=15
    )
    resp.raise_for_status()
    resp.encoding = "utf-8"

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []
    for item in soup.select("div.result, div.c-container")[:SEARCH_RESULTS_PER_QUERY]:
        title_el = item.select_one("h3 a, .t a")
        snippet_el = item.select_one(
            ".c-abstract, .content-right_8Zs40, span.content-right_8Zs40, .c-span9"
        )
        url_el = item.select_one("h3 a")
        if not title_el:
            continue
        results.append({
            "title": title_el.get_text(strip=True),
            "url": url_el.get("href", "") if url_el else "",
            "snippet": snippet_el.get_text(strip=True)[:400] if snippet_el else "",
        })
    logger.info(f"Baidu scrape '{query}' → {len(results)} results")
    return results


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    if tool_name == "search_market":
        return _search_market(**tool_input)
    elif tool_name == "search_product_detail":
        return _search_product_detail(**tool_input)
    elif tool_name == "get_current_date":
        return json.dumps({"date": date.today().isoformat()}, ensure_ascii=False)
    else:
        return json.dumps({"error": f"未知工具: {tool_name}"}, ensure_ascii=False)


def _search_market(query: str, focus: str) -> str:
    site_filter = _FOCUS_TO_SITE.get(focus, "")
    full_query = f"{query} {site_filter}" if site_filter else query
    try:
        items = _do_search(full_query)
        logger.info(f"search_market '{query}' ({focus}) → {len(items)} results")
        return json.dumps(
            {"query": query, "focus": focus, "results": items}, ensure_ascii=False
        )
    except Exception as e:
        logger.error(f"search_market failed: {e}")
        return json.dumps({"error": str(e), "query": query}, ensure_ascii=False)


def _search_product_detail(product_name: str, aspect: str) -> str:
    query_template = _ASPECT_TO_QUERY.get(aspect, "{product} " + aspect)
    query = query_template.format(product=product_name)
    site_filter = _ASPECT_TO_SITE.get(aspect, "")
    full_query = f"{query} {site_filter}" if site_filter else query
    try:
        items = _do_search(full_query)
        logger.info(f"search_product_detail '{product_name}' ({aspect}) → {len(items)} results")
        return json.dumps(
            {"product": product_name, "aspect": aspect, "query": query, "results": items},
            ensure_ascii=False,
        )
    except Exception as e:
        logger.error(f"search_product_detail failed: {e}")
        return json.dumps(
            {"error": str(e), "product": product_name}, ensure_ascii=False
        )
