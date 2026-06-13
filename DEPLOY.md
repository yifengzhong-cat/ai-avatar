# ☁️ AI数字分身 - 云部署指南

> 5分钟部署到 Streamlit Cloud，免费！朋友打开链接就能用。

## 📋 前提条件

- 一个 GitHub 账号（[github.com](https://github.com) 免费注册）
- 代码已推送到 GitHub 仓库

## 🚀 部署步骤（跟着做就行）

### 第一步：创建 GitHub 仓库

```bash
cd /home/yifeng/ai-operation

# 初始化 Git
git init
git add .
git commit -m "AI数字分身 v1.2 - 支持云部署"
```

然后去 GitHub 创建一个新仓库（比如叫 `ai-digital-avatar`），把代码推上去：

```bash
git remote add origin https://github.com/你的用户名/仓库名.git
git branch -M main
git push -u origin main
```

### 第二步：部署到 Streamlit Cloud

1. 打开 [share.streamlit.io](https://share.streamlit.io)
2. 用 GitHub 账号登录
3. 点击 **「New app」**
4. 选择你刚才的仓库
5. Branch：`main`
6. Main file path：`app/main.py`
7. 点击 **「Deploy!」**

### 第三步：配置 Secrets（重要！）

部署成功后，还需要设置 API Key 等敏感信息：

1. 进入你的 App 页面
2. 点击右上角 **「⋮」→「Settings」→「Secrets」**
3. 粘贴以下内容：

```toml
OPENAI_API_KEY = "sk-你的DeepSeek-Key"
OPENAI_BASE_URL = "https://api.deepseek.com/v1"
LLM_MODEL = "deepseek-chat"
MY_NAME = "运营小能手"
MY_NICHE = "短视频运营"
MY_STYLE = "幽默接地气，擅长用生活化比喻"
APP_PASSWORD = "aigod123"
```

4. 点击 **Save**，App 会自动重启

### 第四步：分享给朋友

App 的链接格式是：
```
https://你的用户名-streamlit-ai-xxx-xxx.streamlit.app
```

把链接发给朋友，告诉他们密码是 `aigod123`（或在 Secrets 里改成你自定义的密码）。

## 🔒 安全提示

- **永远不要**把 API Key 放在代码里提交到 GitHub
- Secrets 只在 Streamlit Cloud 后台设置，不会公开
- 密码可以随时在 Secrets 里修改，App 自动生效
- 如果发现 API 用量异常，去 DeepSeek 后台换 Key

## 🔄 更新代码

本地改了代码后，推送即可自动部署：

```bash
git add .
git commit -m "更新了XX功能"
git push
# Streamlit Cloud 自动检测并重新部署！
```

## 💰 费用估算

| 项目 | 费用 |
|------|------|
| Streamlit Cloud 托管 | **免费** |
| DeepSeek API 调用 | **~¥0.14/百万token** |
| 10个人每天各用5次 | **约 ¥1-2/天** |
| 一个月总成本 | **约 ¥30-50** |

## 🆘 问题排查

| 问题 | 解决 |
|------|------|
| App显示"API Key未配置" | 检查 Secrets 设置里的OPENAI_API_KEY |
| 密码不对 | 检查 Secrets 里的APP_PASSWORD |
| 部署失败 | 在Streamlit Cloud点「Reboot」重启 |
| 想看日志 | 点「⋮」→「Settings」→「Logs」 |

---

有部署问题直接把报错丢给AI问就行～
