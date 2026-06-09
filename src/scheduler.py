import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from rich.console import Console

from src.config import settings

console = Console()
logger = logging.getLogger(__name__)


def run_job():
    from src.agent import run_daily_research
    from src.report import generate_reports

    console.print("[bold cyan]开始每日选品研究...[/bold cyan]")

    try:
        data = run_daily_research()
        md_path, json_path = generate_reports(data)
        console.print("[bold green]报告生成完成！[/bold green]")
        console.print(f"  Markdown: [underline]{md_path}[/underline]")
        console.print(f"  JSON:     [underline]{json_path}[/underline]")
    except Exception as e:
        logger.exception(f"Daily job failed: {e}")
        console.print(f"[bold red]任务失败: {e}[/bold red]")


def start_scheduler():
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    trigger = CronTrigger(
        hour=settings.schedule_hour,
        minute=settings.schedule_minute,
        timezone="Asia/Shanghai",
    )
    scheduler.add_job(run_job, trigger=trigger, id="daily_recommendation")

    console.print(
        f"[cyan]定时任务已启动，每天北京时间 "
        f"[bold]{settings.schedule_hour:02d}:{settings.schedule_minute:02d}[/bold] 自动运行[/cyan]"
    )
    console.print("[dim]按 Ctrl+C 停止[/dim]")

    try:
        scheduler.start()
    except KeyboardInterrupt:
        console.print("[yellow]定时任务已停止。[/yellow]")
