# 淘宝选品推荐 Agent

每天自动帮你在 **纸品** 和 **家清个护** 两个品类里寻找可以实际卖出去的爆款产品，
生成带六维评分、进货价/售价、行动建议的选品日报。专为零电商经验的店主设计。

> 示例报告见 [`docs/sample_report.md`](docs/sample_report.md)

---

## 它能做什么

每次运行，Agent 会：
1. 联网搜索两个品类的当日市场趋势和竞争格局
2. 识别 3-5 个有潜力的候选产品
3. 查 1688 进货价、淘宝竞争、消费者需求
4. 按六维度打分（搜索热度/竞争烈度/利润空间/复购率/差异化/季节性）
5. 输出 Top 5 推荐 + 建议回避清单，每个产品附带**具体行动建议**

---

## 快速开始（在你自己的电脑上运行）

> 注意：本项目需要联网访问硅基流动和搜索引擎，请在你自己的电脑或服务器上运行。

```bash
# 1. 安装依赖（需先装好 Python 3.11+）
pip install -r requirements.txt

# 2. 创建配置文件
cp .env.example .env
```

编辑 `.env`，填入你的 Key：

```ini
# LLM —— 硅基流动（注册送 ¥14 免费额度，https://siliconflow.cn）
LLM_API_KEY=你的硅基流动Key

# 搜索 —— Serper（注册送 2500 次免费，https://serper.dev）
# 如果留空不填，会自动改用百度网页抓取（免Key，但稳定性略低）
SERPER_API_KEY=你的SerperKey
```

```bash
# 3. 验证配置和网络
python main.py validate

# 4. 立即跑一次（报告生成在 reports/ 目录）
python main.py run

# 5. 启动每日定时（每天北京时间 08:00 自动运行）
python main.py schedule
```

---

## 三个命令

| 命令 | 作用 |
|------|------|
| `python main.py validate` | 检查 API Key 和网络连通性 |
| `python main.py run` | 立即运行一次，生成今日报告 |
| `python main.py schedule` | 启动守护进程，每天定时自动运行 |

---

## 切换 LLM / 搜索引擎

只改 `.env`，代码无需改动：

**LLM（任选其一）：**
| 服务商 | 配置 |
|--------|------|
| 硅基流动 Qwen | `MODEL=Qwen/Qwen2.5-72B-Instruct`（默认） |
| 硅基流动 DeepSeek | `MODEL=deepseek-ai/DeepSeek-V3` |
| DeepSeek 官方 | `LLM_BASE_URL=https://api.deepseek.com/v1` `MODEL=deepseek-chat` |

**搜索（任选其一）：**
- 填 `SERPER_API_KEY` → 用 Serper（Google 结果，质量高）
- 留空 → 自动用百度网页抓取（免 Key）

---

## 目录结构

```
├── main.py              # CLI 入口
├── src/
│   ├── config.py        # 品类定义、评分权重
│   ├── tools.py         # 搜索工具（Serper / 百度）
│   ├── agent.py         # LLM 多轮研究循环
│   ├── report.py        # Markdown / JSON 报告生成
│   └── scheduler.py     # 每日定时
├── scripts/
│   └── demo_report.py   # 生成样例报告（演示格式）
├── reports/             # 每日报告输出目录
└── docs/sample_report.md  # 示例报告
```

---

## 关于"真实卖出去"

选品逻辑专门针对新手优化，每个推荐都考虑了**可落地性**：

- **优先高频复购品**（纸品、家清都是消耗品，老客自然回购）
- **避开大牌垄断的标品**（普通卷纸、大桶洗衣液打不过维达/蓝月亮）
- **选轻便好快递的细分款**（降低运费和压货风险）
- **每个产品给出差异化卖点和文案方向**（帮你做出有竞争力的商品页）
- **明确标注风险和回避清单**（少踩坑）

报告只是第一步。拿到推荐后，建议小批量试款（每款进货成本控制在 200 元内），
跑一两周数据看真实转化，再决定加码哪款。
