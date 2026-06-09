import json
import logging
from datetime import date
from typing import Any

from src.config import settings, SEARCH_RESULTS_PER_QUERY

logger = logging.getLogger(__name__)

TOOL_SCHEMAS = [
    {
        "name": "search_market",
        "description": (
            "搜索中国电商市场数据，获取热销产品、销量趋势、品类整体动态。"
            "适合用于品类整体研究。搜索覆盖淘宝、1688、百度、小红书。"
        ),
        "input_schema": {
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
    {
        "name": "search_product_detail",
        "description": (
            "对特定产品进行深度研究，获取1688供货价、竞争对手数量、"
            "消费者需求和差异化机会。在识别候选产品后使用此工具。"
        ),
        "input_schema": {
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
    {
        "name": "get_current_date",
        "description": "返回今天的日期，用于季节性分析和时效性判断。",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
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

_ASPECT_TO_DOMAINS = {
    "supplier_pricing": ["1688.com", "taobao.com"],
    "competitor_analysis": ["taobao.com", "tmall.com", "jd.com"],
    "consumer_demand": ["baidu.com", "xiaohongshu.com", "zhihu.com"],
    "differentiation": ["xiaohongshu.com", "zhihu.com", "baidu.com"],
}


def _get_tavily_client():
    from tavily import TavilyClient
    return TavilyClient(api_key=settings.tavily_api_key)


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
    client = _get_tavily_client()
    domains = _FOCUS_TO_DOMAINS.get(focus, [])
    try:
        result = client.search(
            query=query,
            search_depth="advanced",
            max_results=SEARCH_RESULTS_PER_QUERY,
            include_domains=domains if domains else None,
            include_raw_content=False,
        )
        items = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", "")[:400],
            }
            for r in result.get("results", [])
        ]
        logger.info(f"search_market '{query}' → {len(items)} results")
        return json.dumps(
            {"query": query, "focus": focus, "results": items}, ensure_ascii=False
        )
    except Exception as e:
        logger.error(f"search_market failed: {e}")
        return json.dumps({"error": str(e), "query": query}, ensure_ascii=False)


def _search_product_detail(product_name: str, aspect: str) -> str:
    client = _get_tavily_client()
    query_template = _ASPECT_TO_QUERY.get(aspect, "{product} " + aspect)
    query = query_template.format(product=product_name)
    domains = _ASPECT_TO_DOMAINS.get(aspect, [])
    try:
        result = client.search(
            query=query,
            search_depth="advanced",
            max_results=SEARCH_RESULTS_PER_QUERY,
            include_domains=domains if domains else None,
            include_raw_content=False,
        )
        items = [
            {
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "snippet": r.get("content", "")[:400],
            }
            for r in result.get("results", [])
        ]
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
