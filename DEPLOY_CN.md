# ☁️ AI数字分身 - 国内可访问云部署指南

> 三种方案任选，确保国内访问畅通 🇨🇳

---

## 📊 方案对比

| 方案 | 费用 | 国内访问 | 难度 | 推荐 |
|------|------|---------|------|------|
| **Railway** | ~$5/月 | ⭐⭐⭐⭐ 良好 | ⭐ 极简 | 🥇推荐 |
| **阿里云SAE** | ~¥50/月 | ⭐⭐⭐⭐⭐ 极佳 | ⭐⭐ 简单 | 🥈推荐 |
| **Hugging Face** | 免费 | ⭐⭐⭐ 尚可 | ⭐ 极简 | 🥉备用 |

---

## 🚀 方案一：Railway（推荐，最省心）

Railway 在国内有较好的访问速度，且部署极简。

### 1. 准备代码

把项目推送到 GitHub（确保 `.gitignore` 生效，`.env` 不提交）：

```bash
cd /home/yifeng/ai-operation
git init
git add .
git commit -m "AI数字分身 v2.0"

# 创建GitHub仓库后
git remote add origin https://github.com/你的用户名/ai-avatar.git
git push -u origin main
```

### 2. 部署到 Railway

1. 打开 [railway.app](https://railway.app) → 用 GitHub 登录
2. 点击 **「New Project」→「Deploy from GitHub repo」**
3. 选择你的仓库
4. Railway 会自动检测 Dockerfile 并构建

### 3. 配置环境变量

在 Railway Dashboard → 你的项目 → **Variables** 添加：

```
OPENAI_API_KEY=sk-你的DeepSeek-Key
OPENAI_BASE_URL=https://api.deepseek.com/v1
LLM_MODEL=deepseek-chat
MY_NAME=运营小能手
MY_NICHE=短视频运营
MY_STYLE=幽默接地气，擅长用生活化比喻
APP_PASSWORD=aigod123
```

### 4. 获取域名

Railway 会分配一个 `xxx.up.railway.app` 域名，也可绑定自己的域名。

把链接发给朋友，输入密码就能用！

---

## 🇨🇳 方案二：阿里云SAE（国内最快）

阿里云 Serverless 应用引擎，国内访问速度最快。

### 1. 构建并推送镜像

```bash
# 构建Docker镜像
docker build -t ai-avatar .

# 推送到阿里云容器镜像服务（免费）
# 1. 打开 https://cr.console.aliyun.com
# 2. 创建命名空间和镜像仓库
# 3. 按指引登录并推送

docker tag ai-avatar registry.cn-hangzhou.aliyuncs.com/你的命名空间/ai-avatar:v1
docker push registry.cn-hangzhou.aliyuncs.com/你的命名空间/ai-avatar:v1
```

### 2. 创建SAE应用

1. 打开 [sae.console.aliyun.com](https://sae.console.aliyun.com)
2. 创建应用 → 选择「容器镜像部署」
3. 选择刚才推送的镜像
4. 配置环境变量（同方案一的变量列表）
5. 端口设置：8501
6. 点击创建

### 3. 绑定域名（可选）

SAE 默认提供 `xxx.cn-hangzhou.sae.aliyun.com` 域名。

如需自定义域名，在「域名管理」中绑定并配置DNS。

### 💰 费用估算

- SAE 按量付费：约 ¥0.5/天（低配）+ ¥1-2/天 API 调用
- 一个月总成本：约 ¥50-80

---

## 🆓 方案三：Hugging Face Spaces（免费备用）

完全免费，但国内访问偶尔较慢。

### 1. 创建Space

1. 打开 [huggingface.co/spaces](https://huggingface.co/spaces)
2. 点击 **「Create new Space」**
3. SDK 选择 **「Streamlit」**
4. 选择 **「Docker」** 而不是 Streamlit template
5. Space Name：`ai-avatar`

### 2. 上传代码

```bash
# 克隆Space仓库
git clone https://huggingface.co/spaces/你的用户名/ai-avatar
cd ai-avatar

# 复制项目文件
cp -r /home/yifeng/ai-operation/* .

# 提交并推送
git add .
git commit -m "Deploy AI 数字分身"
git push
```

### 3. 配置Secrets

在 Hugging Face Space → **Settings → Repository Secrets** 添加：

```
OPENAI_API_KEY = sk-你的Key
OPENAI_BASE_URL = https://api.deepseek.com/v1
LLM_MODEL = deepseek-chat
MY_NAME = 运营小能手
MY_NICHE = 短视频运营
MY_STYLE = 幽默接地气，擅长用生活化比喻
APP_PASSWORD = aigod123
```

自动重新部署完成。访问地址：`https://huggingface.co/spaces/你的用户名/ai-avatar`

---

## 🐳 Docker本地部署（测试用）

```bash
# 构建
docker build -t ai-avatar .

# 运行（挂载.env）
docker run -d \
  --name ai-avatar \
  -p 8501:8501 \
  --env-file .env \
  --restart unless-stopped \
  ai-avatar

# 查看日志
docker logs -f ai-avatar

# 停止
docker stop ai-avatar
```

---

## 🔒 安全提示

- `.env` 文件**永远不要**提交到 Git
- 生产环境用各平台的 Secrets/Variables 管理敏感信息
- 定期更换 `APP_PASSWORD`
- 在 DeepSeek 后台设置 API 用量告警

---

## 🆘 问题排查

| 问题 | 可能原因 | 解决 |
|------|---------|------|
| 国内访问慢 | DNS/CDN | 换阿里云方案或加 CDN |
| 部署后打不开 | 端口没配 | 确认端口配置为 8501 |
| API调用失败 | Key未配置 | 检查环境变量/Secrets |
| 知识库数据丢失 | 容器重启 | 挂载持久化存储卷 |
| ChromaDB加载失败 | 内存不足 | 升级配置至少 1GB 内存 |
| 嵌入模型下载慢 | 网络问题 | 首次启动需下载模型(~400MB)，耐心等待 |

---

选 Railway（推荐）还是阿里云？回复我直接帮你一步步部署 🚀
