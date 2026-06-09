from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    llm_api_key: str = ""
    llm_base_url: str = "https://api.siliconflow.cn/v1"
    tavily_api_key: str = ""
    report_dir: Path = Path("./reports")
    schedule_hour: int = 8
    schedule_minute: int = 0
    log_level: str = "INFO"
    model: str = "Qwen/Qwen2.5-72B-Instruct"
    max_tokens: int = 8192
    max_agent_turns: int = 20


settings = Settings()

CATEGORIES = {
    "纸品": {
        "name_en": "Paper Products",
        "products": ["卷纸", "抽纸", "湿巾", "厨房纸", "纸尿裤"],
        "search_keywords": [
            "淘宝卷纸爆款热销",
            "抽纸热销款推荐",
            "湿巾淘宝新品",
            "纸尿裤爆款品牌",
            "厨房纸热销推荐",
        ],
    },
    "家清个护": {
        "name_en": "Household Cleaning & Personal Care",
        "products": ["洗衣液", "洗洁精", "沐浴露", "洗发水", "消毒液", "牙膏"],
        "search_keywords": [
            "洗衣液淘宝爆款",
            "沐浴露热销新品",
            "洗发水推荐热销",
            "消毒液淘宝畅销",
            "牙膏爆款推荐",
        ],
    },
}

SCORING_WEIGHTS = {
    "搜索热度": 0.20,
    "竞争烈度": 0.20,
    "利润空间": 0.20,
    "复购率潜力": 0.15,
    "差异化机会": 0.15,
    "季节性时效性": 0.10,
}

SCORE_THRESHOLD = 6.0
TOP_N_PRODUCTS = 5
SEARCH_RESULTS_PER_QUERY = 7
