import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

from src.config import settings, SCORING_WEIGHTS

logger = logging.getLogger(__name__)


def generate_reports(data: dict[str, Any]) -> tuple[Path, Path]:
    settings.report_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    base_name = f"recommendation_{today}"
    md_path = settings.report_dir / f"{base_name}.md"
    json_path = settings.report_dir / f"{base_name}.json"

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    logger.info(f"JSON report: {json_path}")

    md_content = _render_markdown(data, today)
    md_path.write_text(md_content, encoding="utf-8")
    logger.info(f"Markdown report: {md_path}")

    return md_path, json_path


def _render_markdown(data: dict[str, Any], today: str) -> str:
    lines: list[str] = []

    lines += [
        f"# 淘宝每日选品推荐报告",
        f"",
        f"**生成日期：** {today}",
        f"**分析品类：** 纸品 | 家清个护",
        f"",
        f"---",
        f"",
    ]

    if "error" in data and "categories" not in data:
        lines += [
            f"## ⚠️ 报告生成异常",
            f"",
            f"```",
            str(data),
            f"```",
        ]
        return "\n".join(lines)

    if "raw_text" in data:
        lines += [
            f"## ⚠️ JSON解析失败，原始输出如下",
            f"",
            data["raw_text"],
        ]
        return "\n".join(lines)

    categories = data.get("categories", {})

    for cat_name, cat_data in categories.items():
        lines += [f"## 品类：{cat_name}", f""]

        insight = cat_data.get("category_insight", "")
        if insight:
            lines += [f"> {insight}", f""]

        products = cat_data.get("top_products", [])
        for product in products:
            rank = product.get("rank", "?")
            name = product.get("product_name", "未知产品")
            name_en = product.get("product_name_en", "")
            w_score = product.get("weighted_score", 0)
            comp = product.get("competition_level", "")

            comp_label = {"low": "🟢 低", "medium": "🟡 中", "high": "🔴 高"}.get(comp, comp)

            lines += [
                f"### #{rank}  {name}  ({name_en})",
                f"",
                f"**综合评分：{w_score:.1f} / 10**　｜　竞争强度：{comp_label}",
                f"",
            ]

            scores = product.get("scores", {})
            lines += [
                f"| 评分维度 | 得分 | 权重 | 加权分 |",
                f"|---------|:----:|:----:|:------:|",
            ]
            for dim, weight in SCORING_WEIGHTS.items():
                score = scores.get(dim, 0)
                lines.append(f"| {dim} | {score}/10 | {weight:.0%} | {score * weight:.2f} |")
            lines.append("")

            supply = product.get("supply_price_range", "待查")
            retail = product.get("suggested_retail_price", "待定")
            margin = product.get("estimated_margin_pct", "")
            lines += [
                f"**参考进货价（1688）：** {supply}",
                f"**建议售价：** {retail}",
            ]
            if margin:
                lines.append(f"**预估利润率：** {margin}")
            lines.append("")

            ksp = product.get("key_selling_points", [])
            if ksp:
                lines.append("**核心卖点：**")
                for pt in ksp:
                    lines.append(f"- {pt}")
                lines.append("")

            target = product.get("target_customer", "")
            if target:
                lines += [f"**目标客群：** {target}", ""]

            action = product.get("action_recommendation", "")
            if action:
                lines += [f"**行动建议：**", f"", f"> {action}", ""]

            risk = product.get("risk_warning", "")
            if risk:
                lines += [f"**风险提示：** ⚠️ {risk}", ""]

            sources = product.get("data_sources", [])
            if sources:
                lines += [f"**数据来源：** {' | '.join(sources[:3])}", ""]

            lines += ["---", ""]

        avoid = cat_data.get("avoid_products", [])
        if avoid:
            lines += [f"### 本期建议回避产品", ""]
            for item in avoid:
                lines.append(f"- {item}")
            lines.append("")

    notes = data.get("agent_notes", "")
    if notes:
        lines += [f"## 分析师备注", f"", notes, ""]

    lines += [
        "---",
        "*本报告由AI选品顾问自动生成，仅供参考。最终决策请结合实际市场情况判断。*",
    ]

    return "\n".join(lines)
