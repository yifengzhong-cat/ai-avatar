# 🤖 AI数字分身 - 短视频运营智能助手

> 为你自己打造一个AI数字分身，让它帮你写脚本、追热点、改文案、分析数据。

## 🎯 这是什么？

一个专为**短视频运营**打造的AI工具集。你只需要配置好API Key，就能拥有一个懂你风格、帮你干活的AI助手。

**适合谁用？**
- 短视频运营（抖音/小红书/视频号/B站）
- AI小白（不需要任何编程基础）
- 想做AI+垂直领域运营的人

## 🧩 功能模块

| 模块 | 功能 | 使用场景 |
|------|------|---------|
| 🎬 **脚本生成器** | 生成完整短视频脚本 | 没灵感时、批量产出时 |
| 🔥 **热点分析** | 分析热点+推荐选题 | 追热点、策划内容方向 |
| ✍️ **内容改写** | 一键适配不同平台 | 一条内容多平台分发 |
| 📊 **数据分析** | 诊断视频数据 | 复盘优化、提升数据 |
| 💬 **数字分身对话** | 用你的风格聊天 | 日常运营答疑 |

## 🚀 快速开始（5分钟）

### 第一步：安装Python依赖

```bash
# 进入项目目录
cd ai-operation

# 安装依赖
pip install -r requirements.txt
```

### 第二步：配置API Key

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件（用任意文本编辑器）
nano .env  # 或用 vim / vscode
```

在 `.env` 文件中填入你的API Key：

```env
# 必填：你的API Key
OPENAI_API_KEY=sk-你的key

# 选填：根据你用的服务商修改
# 用DeepSeek（推荐，超便宜）
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat

# 用通义千问
# OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# LLM_MODEL=qwen-plus

# 填你的个人设定
MY_NAME=你的名字
MY_NICHE=短视频运营
MY_STYLE=幽默接地气，擅长用生活化比喻
```

### 🟢 推荐：用DeepSeek（最便宜）

1. 打开 [platform.deepseek.com](https://platform.deepseek.com/)
2. 注册账号，充值 ¥1 起
3. 在「API Keys」页面创建Key
4. 价格：约 ¥0.14/百万token，每天用也就几毛钱

其他可选：
- [通义千问](https://dashscope.aliyun.com/) - 阿里云
- [智谱AI](https://open.bigmodel.cn/) - 清华系
- [Moonshot](https://platform.moonshot.cn/) - Kimi

### 第三步：启动

```bash
streamlit run app/main.py
```

浏览器打开 http://localhost:8501 就能用了！

或用一键脚本：
```bash
bash setup.sh
```

## 📁 项目结构

```
ai-operation/
├── README.md              # 你正在看的文档
├── .env.example           # 配置模板（复制为.env）
├── requirements.txt       # Python依赖
├── setup.sh              # 一键安装启动脚本
├── app/
│   ├── main.py           # 🎯 主界面（Streamlit）
│   ├── tools/            # 🧰 AI工具集
│   │   ├── script_writer.py     # 脚本生成
│   │   ├── trend_analyzer.py    # 热点分析
│   │   ├── content_rewriter.py  # 内容改写
│   │   └── data_analyzer.py     # 数据分析
│   └── utils/            # ⚙️ 工具函数
│       ├── config.py     # 配置管理
│       └── prompts.py    # 提示词模板
└── data/                 # 数据存储
```

## 🎓 AI小白入门指南

### 什么是API Key？

API Key就像一把钥匙，让你能调用大模型（类似ChatGPT）的能力。你需要：
1. 去大模型服务商注册账号
2. 获取一个API Key（通常是一串以`sk-`开头的字符）
3. 把它填到`.env`文件中
4. 用多少花多少，按量付费

### 推荐学习路径

| 阶段 | 目标 | 操作 |
|------|------|------|
| 第1天 | 跑起来 | 配置DeepSeek Key，用"脚本生成器"生成第一条脚本 |
| 第1周 | 熟练用 | 每天用"热点分析"策划选题，用"内容改写"做分发 |
| 第2周 | 调风格 | 修改`.env`里的`MY_STYLE`，让AI更像你 |
| 第1月 | 进阶 | 看`prompts.py`，修改提示词让输出更贴合你的需求 |

### 常见问题

**Q: 需要会编程吗？**
A: 不需要。按照上面的步骤装好就能用。如果卡住了，把报错信息丢给ChatGPT/Claude问就行。

**Q: 要花多少钱？**
A: 用DeepSeek的话，每天正常使用大约几毛钱，一个月十几块就够。

**Q: 生成的内容能用吗？**
A: AI生成的是初稿，建议你在此基础上做微调。80% AI + 20% 人工 = 最佳效果。

**Q: 怎么让AI写得更像我？**
A: 编辑`.env`中的`MY_STYLE`，描述越具体越好。同时可以在`app/utils/prompts.py`中调优提示词。

**Q: 能接入抖音/小红书后台数据吗？**
A: 目前是手动输入数据让AI分析。自动接入需要各平台的开放API权限，后续可以扩展。

## 🔧 进阶DIY

### 调整AI风格

编辑 `app/utils/prompts.py`，找到 `PERSONA_SYSTEM_PROMPT`，修改人设描述。

### 添加新功能

在 `app/tools/` 目录下创建新文件，然后在 `app/main.py` 中导入即可。

例如想加一个「标题打分器」：
```python
# app/tools/title_scorer.py
def score_title(title: str) -> str:
    # 你的评分逻辑
    pass
```

### 换用不同模型

修改 `.env` 中的 `LLM_MODEL` 即可，支持所有OpenAI兼容接口的模型。

## 📝 更新计划

- [ ] 对话历史保存
- [ ] 批量脚本生成
- [ ] 竞品账号分析
- [ ] 视频画面描述生成
- [ ] 自动发布（需平台API）

---

Made with ❤️ for creators | 有问题就找AI问
