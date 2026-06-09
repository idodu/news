#!/usr/bin/env python3
"""
淘宝选品推荐 Agent — CLI 入口

用法:
    python main.py run        # 立即运行一次（测试/手动触发）
    python main.py schedule   # 启动每日定时运行（北京时间 08:00）
    python main.py validate   # 验证 API Key 和网络连通性
"""
import argparse
import logging
import sys


def _setup_logging(level: str = "INFO"):
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def cmd_run(_args):
    from src.config import settings
    _setup_logging(settings.log_level)

    from rich.console import Console
    console = Console()

    from src.agent import run_daily_research
    from src.report import generate_reports

    console.print("[bold cyan]正在运行选品研究（单次）...[/bold cyan]")
    data = run_daily_research()
    md_path, json_path = generate_reports(data)
    console.print(f"\n[bold green]完成！[/bold green]")
    console.print(f"  Markdown 报告: [underline]{md_path}[/underline]")
    console.print(f"  JSON 数据:     [underline]{json_path}[/underline]")


def cmd_schedule(_args):
    from src.config import settings
    _setup_logging(settings.log_level)

    from src.scheduler import start_scheduler
    start_scheduler()


def cmd_validate(_args):
    _setup_logging("INFO")

    from rich.console import Console
    console = Console()

    console.print("[bold]检查配置...[/bold]")
    from src.config import settings

    if not settings.llm_api_key:
        console.print("[red]错误：LLM_API_KEY 未设置（在 .env 中填入硅基流动 API Key）[/red]")
        sys.exit(1)
    if not settings.tavily_api_key:
        console.print("[red]错误：TAVILY_API_KEY 未设置[/red]")
        sys.exit(1)

    console.print(f"  模型:       {settings.model}")
    console.print(f"  API地址:    {settings.llm_base_url}")
    console.print(f"  报告目录:   {settings.report_dir}")
    console.print(f"  定时时间:   每天北京时间 {settings.schedule_hour:02d}:{settings.schedule_minute:02d}")

    console.print("\n[bold]测试 Tavily API...[/bold]")
    from tavily import TavilyClient
    tc = TavilyClient(api_key=settings.tavily_api_key)
    result = tc.search("淘宝卷纸热销", max_results=1)
    count = len(result.get("results", []))
    console.print(f"  [green]Tavily OK[/green] — 返回 {count} 条结果")

    console.print("\n[bold]测试 LLM API...[/bold]")
    from openai import OpenAI
    client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    msg = client.chat.completions.create(
        model=settings.model,
        max_tokens=10,
        messages=[{"role": "user", "content": "hi"}],
    )
    finish = msg.choices[0].finish_reason
    console.print(f"  [green]LLM API OK[/green] — finish_reason: {finish}")

    console.print("\n[bold green]所有检查通过！可以运行 python main.py run 测试完整流程。[/bold green]")


def main():
    parser = argparse.ArgumentParser(
        description="淘宝选品推荐 Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command")
    sub.required = True

    sub.add_parser("run", help="立即运行一次选品研究")
    sub.add_parser("schedule", help="启动每日定时任务（北京时间 08:00）")
    sub.add_parser("validate", help="验证 API Key 和网络连通性")

    args = parser.parse_args()
    {"run": cmd_run, "schedule": cmd_schedule, "validate": cmd_validate}[args.command](args)


if __name__ == "__main__":
    main()
