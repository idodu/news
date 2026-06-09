import json
import logging
from datetime import date
from typing import Any

import anthropic

from src.config import settings, CATEGORIES, SCORING_WEIGHTS, TOP_N_PRODUCTS
from src.tools import TOOL_SCHEMAS, execute_tool

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一位专业的淘宝电商选品顾问，专门帮助零经验的小店主在以下两个品类中发现可以实际卖出去的爆款产品：

**品类一：纸品**（卷纸、抽纸、湿巾、厨房纸、纸尿裤）
**品类二：家清个护**（洗衣液、洗洁精、沐浴露、洗发水、消毒液、牙膏）

## 你的工作流程

**第一步：品类趋势调研**
- 对"纸品"和"家清个护"各做1次 search_market（focus=trending），了解整体市场热度
- 再各做1次 search_market（focus=competition），了解竞争格局

**第二步：识别候选产品**
- 每个品类找出3-5个有潜力的具体产品

**第三步：候选产品深度研究**
- 对每个候选产品，至少做2次 search_product_detail：
  - 一次 supplier_pricing（了解1688进货价）
  - 一次 consumer_demand（了解消费者需求）
  - 可选：differentiation（差异化机会）

**第四步：综合评分和输出**
- 按六维评分体系为每个产品打分
- 输出JSON格式报告

## 六维评分标准（各1-10分）

| 维度 | 说明 | 高分条件 |
|------|------|---------|
| 搜索热度 | 消费者搜索和购买热度 | 近期搜索量高、上升趋势 |
| 竞争烈度 | 分越高=竞争越少=越好 | 淘宝卖家少、大牌未布局 |
| 利润空间 | 1688进价到淘宝售价的差价 | 利润率30%以上得8+分 |
| 复购率潜力 | 消费者重复购买可能性 | 日用消耗品天然高复购 |
| 差异化机会 | 与竞品区分的可能性 | 有特色卖点、细分人群 |
| 季节性时效性 | 当前时节的需求强度 | 当季需求旺盛 |

加权公式：
- 搜索热度×20% + 竞争烈度×20% + 利润空间×20% + 复购率潜力×15% + 差异化机会×15% + 季节性时效性×10%

## 重要原则

1. 只推荐真正能卖出去的产品，不推荐概念性、难操作的产品
2. 价格区间必须基于实际搜索到的数据，无法获取时标注"数据不足"
3. 行动建议必须具体可操作（首批进货量、定价策略、文案方向）
4. 所有建议考虑到店主是零经验新手
5. 每个品类推荐Top 5，另列出本期建议回避产品

## 最终输出格式

完成所有研究后，用以下JSON格式输出（用```json和```包裹）：

```json
{
  "report_date": "YYYY-MM-DD",
  "categories": {
    "纸品": {
      "top_products": [
        {
          "rank": 1,
          "product_name": "产品名称",
          "product_name_en": "English name",
          "scores": {
            "搜索热度": 8,
            "竞争烈度": 7,
            "利润空间": 8,
            "复购率潜力": 9,
            "差异化机会": 6,
            "季节性时效性": 7
          },
          "weighted_score": 7.6,
          "supply_price_range": "1688参考进货价，例：2-4元/包",
          "suggested_retail_price": "建议零售价，例：8-12元/包",
          "estimated_margin_pct": "预估利润率，例：50-60%",
          "key_selling_points": ["卖点1", "卖点2", "卖点3"],
          "target_customer": "目标客群描述",
          "competition_level": "low",
          "action_recommendation": "具体行动建议：首批进货量、定价策略、主推卖点文案方向",
          "risk_warning": "潜在风险提示",
          "data_sources": ["来源URL1", "来源URL2"]
        }
      ],
      "category_insight": "本品类整体市场洞察，100字以内",
      "avoid_products": ["应避免产品1及原因", "应避免产品2及原因"]
    },
    "家清个护": {
      "top_products": [],
      "category_insight": "",
      "avoid_products": []
    }
  },
  "agent_notes": "本次研究过程的关键发现和注意事项"
}
```
"""


def run_daily_research() -> dict[str, Any]:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    today = date.today().isoformat()
    user_message = (
        f"今天是{today}。请开始今天的淘宝选品研究。\n\n"
        f"需要研究的品类：\n"
        f"1. 纸品（卷纸、抽纸、湿巾、厨房纸、纸尿裤）\n"
        f"2. 家清个护（洗衣液、洗洁精、沐浴露、洗发水、消毒液、牙膏）\n\n"
        f"请按照工作流程，先做品类趋势调研，再对候选产品深度研究，"
        f"每个品类至少做4次搜索，最后输出完整的JSON推荐报告。"
    )

    messages: list[dict] = [{"role": "user", "content": user_message}]
    turn_count = 0

    while turn_count < settings.max_agent_turns:
        turn_count += 1
        logger.info(f"Agent turn {turn_count}/{settings.max_agent_turns}")

        response = client.messages.create(
            model=settings.model,
            max_tokens=settings.max_tokens,
            system=SYSTEM_PROMPT,
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        logger.debug(f"Stop reason: {response.stop_reason}, blocks: {len(response.content)}")
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            return _extract_json_from_response(response.content)

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info(f"Tool call: {block.name}({json.dumps(block.input, ensure_ascii=False)})")
                    result_str = execute_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
            continue

        logger.warning(f"Unexpected stop reason: {response.stop_reason}")
        break

    logger.error(f"Agent loop ended after {turn_count} turns without completing")
    return {"error": "max_turns_exceeded", "turns_used": turn_count}


def _extract_json_from_response(content_blocks: list) -> dict[str, Any]:
    for block in content_blocks:
        if hasattr(block, "text"):
            text = block.text
            start = text.find("```json")
            end = text.rfind("```")
            if start != -1 and end > start:
                json_str = text[start + 7 : end].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse failed: {e}")
                    return {"raw_text": text, "parse_error": str(e)}
    return {"error": "no_json_found"}
