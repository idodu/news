"""
生成一份样例日报，用于演示报告格式。

注意：这里的市场数据是基于行业常识的示例数据，不是实时联网搜索结果。
真实运行时（python main.py run），数据来自 LLM + 联网搜索。

用法：python scripts/demo_report.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.report import generate_reports

SAMPLE_DATA = {
    "report_date": "2026-06-09",
    "categories": {
        "纸品": {
            "category_insight": (
                "夏季湿巾、湿厕纸需求进入旺季；本色竹浆纸因『无添加』健康概念持续走高，"
                "适合新手切入的细分市场。避开大牌正面竞争的卷纸抽纸标品，从场景化、"
                "成分差异化的细分款入手成功率更高。"
            ),
            "top_products": [
                {
                    "rank": 1,
                    "product_name": "湿厕纸（可冲散家庭装）",
                    "product_name_en": "Flushable Wet Toilet Paper",
                    "scores": {
                        "搜索热度": 8, "竞争烈度": 7, "利润空间": 8,
                        "复购率潜力": 9, "差异化机会": 7, "季节性时效性": 8,
                    },
                    "weighted_score": 7.9,
                    "supply_price_range": "3.5-5元/包（40抽，1688 整箱拿货）",
                    "suggested_retail_price": "9.9-15元/包，3包组合装 29.9元",
                    "estimated_margin_pct": "55-65%",
                    "key_selling_points": [
                        "可冲散不堵马桶，解决普通湿巾痛点",
                        "夏季高温清洁需求旺，痔疮/产后人群刚需",
                        "家庭装复购率高，易做老客回购",
                    ],
                    "target_customer": "25-40岁注重个人清洁的女性、母婴家庭、痔疮人群",
                    "competition_level": "medium",
                    "action_recommendation": (
                        "首批进 3-5 箱试款（约 200 元成本），主图突出『可冲散·不堵马桶』，"
                        "做 1 拼 3 组合装拉高客单价。定价 29.9 元/3包，赠湿巾小样引导复购。"
                    ),
                    "risk_warning": "需确认供应商『可冲散』资质，劣质品易投诉；避开维达/洁柔同款正面比价。",
                    "data_sources": ["示例数据（行业常识）"],
                },
                {
                    "rank": 2,
                    "product_name": "本色竹浆抽纸（无漂白）",
                    "product_name_en": "Unbleached Bamboo Pulp Tissue",
                    "scores": {
                        "搜索热度": 7, "竞争烈度": 6, "利润空间": 8,
                        "复购率潜力": 9, "差异化机会": 8, "季节性时效性": 6,
                    },
                    "weighted_score": 7.3,
                    "supply_price_range": "1.2-1.8元/包（1688 整提30包）",
                    "suggested_retail_price": "整箱30包 39.9-49.9元",
                    "estimated_margin_pct": "45-55%",
                    "key_selling_points": [
                        "本色无荧光剂，主打母婴/敏感肌安全",
                        "竹浆可降解，环保概念加分",
                        "日用刚需，整箱购买复购稳定",
                    ],
                    "target_customer": "有婴幼儿的家庭、孕妇、注重环保健康的年轻家庭",
                    "competition_level": "medium",
                    "action_recommendation": (
                        "整箱走量为主，主图强调『无荧光剂·母婴可用』并附检测报告图。"
                        "定价 39.9 元包邮试水，绑定『家庭月度囤货』关键词做搜索流量。"
                    ),
                    "risk_warning": "本色纸偏黄需教育消费者『非脏而是无漂白』，详情页要讲清楚。",
                    "data_sources": ["示例数据（行业常识）"],
                },
                {
                    "rank": 3,
                    "product_name": "厨房吸油纸巾（可撕卷装）",
                    "product_name_en": "Kitchen Oil-Absorbing Paper Towel",
                    "scores": {
                        "搜索热度": 7, "竞争烈度": 7, "利润空间": 7,
                        "复购率潜力": 8, "差异化机会": 6, "季节性时效性": 6,
                    },
                    "weighted_score": 6.9,
                    "supply_price_range": "2-3元/卷（1688）",
                    "suggested_retail_price": "2卷装 16.9元",
                    "estimated_margin_pct": "45-50%",
                    "key_selling_points": [
                        "厨房刚需，可吸油可擦灶台一纸多用",
                        "加厚不掉屑，对标懒人/独居人群",
                        "高频消耗，复购自然",
                    ],
                    "target_customer": "独居青年、家庭主厨、注重厨房清洁的人群",
                    "competition_level": "medium",
                    "action_recommendation": (
                        "做 2 卷起卖拉高客单，主图演示『吸油吸水擦油烟机』三场景。"
                        "搭配洗洁精做关联销售。"
                    ),
                    "risk_warning": "标品竞争偏激烈，靠加厚克重和场景图突围，别打价格战。",
                    "data_sources": ["示例数据（行业常识）"],
                },
            ],
            "avoid_products": [
                "普通卷纸/抽纸标品：维达、清风、洁柔等大牌垄断，新手无价格和流量优势，难盈利。",
                "纸尿裤：单价高、品牌信任门槛高、压货风险大，不适合零经验新手起步。",
            ],
        },
        "家清个护": {
            "category_insight": (
                "洗衣凝珠、衣物除菌液等『升级款』家清产品增速快，利润高于传统洗衣液；"
                "个护中氨基酸沐浴露、泡沫洗手液主打温和概念，复购强。新手宜选小件、"
                "高频、易快递的细分单品，避开大桶洗衣液（重、运费高、利润薄）。"
            ),
            "top_products": [
                {
                    "rank": 1,
                    "product_name": "洗衣凝珠（三合一持久留香）",
                    "product_name_en": "Laundry Detergent Pods",
                    "scores": {
                        "搜索热度": 8, "竞争烈度": 6, "利润空间": 9,
                        "复购率潜力": 9, "差异化机会": 7, "季节性时效性": 7,
                    },
                    "weighted_score": 7.8,
                    "supply_price_range": "0.25-0.4元/颗（1688 散装整袋）",
                    "suggested_retail_price": "52颗罐装 29.9-39.9元",
                    "estimated_margin_pct": "60-70%",
                    "key_selling_points": [
                        "免计量、不沾手，比传统洗衣液体验升级",
                        "三合一（洁净+柔顺+留香）卖点清晰",
                        "轻便好快递，利润率高，复购强",
                    ],
                    "target_customer": "18-35岁年轻租房族、上班族、嫌洗衣液麻烦的人群",
                    "competition_level": "medium",
                    "action_recommendation": (
                        "首批进 1-2 袋散装分装成罐（约 150 元成本，可分装 8-10 罐）。"
                        "主图突出『一颗搞定·持久留香』，做 52 颗罐装定价 29.9 元，"
                        "买二送收纳罐促复购。"
                    ),
                    "risk_warning": "需防儿童误食做好详情页提示；选有香精备案的正规货源。",
                    "data_sources": ["示例数据（行业常识）"],
                },
                {
                    "rank": 2,
                    "product_name": "泡沫洗手液（按压瓶+补充装）",
                    "product_name_en": "Foaming Hand Wash",
                    "scores": {
                        "搜索热度": 7, "竞争烈度": 6, "利润空间": 8,
                        "复购率潜力": 9, "差异化机会": 7, "季节性时效性": 6,
                    },
                    "weighted_score": 7.2,
                    "supply_price_range": "瓶装2-3元 / 补充装1.5元（1688）",
                    "suggested_retail_price": "1瓶+2补充装 24.9元",
                    "estimated_margin_pct": "55-60%",
                    "key_selling_points": [
                        "泡沫绵密温和，主打儿童/敏感肌可用",
                        "补充装模式天然锁定复购",
                        "体积小、好快递、损耗低",
                    ],
                    "target_customer": "母婴家庭、注重卫生的家庭、敏感肌人群",
                    "competition_level": "medium",
                    "action_recommendation": (
                        "用『瓶+补充装』组合切入，主推『买一次用三次』的省钱概念。"
                        "定价 24.9 元，补充装单独上架做复购承接。"
                    ),
                    "risk_warning": "避开舒肤佳/蓝月亮比价区，靠成分温和+套装组合差异化。",
                    "data_sources": ["示例数据（行业常识）"],
                },
                {
                    "rank": 3,
                    "product_name": "衣物除菌液（内衣/婴儿衣物可用）",
                    "product_name_en": "Clothing Sanitizer",
                    "scores": {
                        "搜索热度": 7, "竞争烈度": 7, "利润空间": 8,
                        "复购率潜力": 8, "差异化机会": 7, "季节性时效性": 8,
                    },
                    "weighted_score": 7.4,
                    "supply_price_range": "4-6元/瓶（1688）",
                    "suggested_retail_price": "2瓶装 39.9元",
                    "estimated_margin_pct": "50-60%",
                    "key_selling_points": [
                        "梅雨/夏季衣物除菌防霉刚需",
                        "母婴衣物、内衣单独除菌的细分需求",
                        "搭配洗衣液/凝珠做关联销售",
                    ],
                    "target_customer": "母婴家庭、注重健康的家庭、南方潮湿地区用户",
                    "competition_level": "medium",
                    "action_recommendation": (
                        "抓住 6-8 月潮湿季节窗口，主图打『除菌99.9%·母婴衣物可用』。"
                        "和洗衣凝珠做关联推荐，提升连带率。"
                    ),
                    "risk_warning": "除菌宣称需有检测依据，文案别写『杀菌/消毒』等违规医疗用语。",
                    "data_sources": ["示例数据（行业常识）"],
                },
            ],
            "avoid_products": [
                "大桶装洗衣液（3kg以上）：重、运费高、利润被快递吃掉，且大牌价格战激烈。",
                "洗发水：成分信任门槛高、退货率高，新手难建立专业信任，不宜首选。",
            ],
        },
    },
    "agent_notes": (
        "本报告为【样例数据】，用于演示报告格式与分析维度，非实时联网结果。"
        "真实运行（python main.py run）时，所有数据来自 LLM 结合 Serper 联网搜索的当日市场情报。"
        "选品逻辑：新手优先选『高频复购 + 轻便好快递 + 可差异化』的细分单品，"
        "避开大牌垄断的标品和高压货风险品类。"
    ),
}

if __name__ == "__main__":
    md_path, json_path = generate_reports(SAMPLE_DATA)
    print(f"样例报告已生成：")
    print(f"  Markdown: {md_path}")
    print(f"  JSON:     {json_path}")
