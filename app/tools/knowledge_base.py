"""
AI数字分身 - RAG知识库
基于ChromaDB向量数据库，支持文档上传（txt/md/json/pdf）、检索、注入AI生成

使用方式:
    kb = KnowledgeBase()
    kb.add_document("我的爆款脚本合集", "内容...", category="脚本模板")
    results = kb.search("怎么做口播开头", top_k=3)
    context = kb.format_context(results)  # 注入到AI提示词
"""
import os
import hashlib
from datetime import datetime
from typing import Optional
import io

from langchain_text_splitters import RecursiveCharacterTextSplitter

# ChromaDB
import chromadb
from chromadb.config import Settings as ChromaSettings

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
CHROMA_DIR = os.path.join(DATA_DIR, "chromadb")
os.makedirs(CHROMA_DIR, exist_ok=True)

# ============================================
# 文件解析工具
# ============================================
SUPPORTED_EXTENSIONS = [".txt", ".md", ".json", ".pdf"]


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    """
    从上传文件中提取文本内容
    支持：txt, md, json, pdf

    参数:
        filename: 文件名
        file_bytes: 文件字节内容

    返回:
        提取的文本内容
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".pdf":
        return _extract_pdf_text(file_bytes)
    elif ext in (".txt", ".md", ".json"):
        return file_bytes.decode("utf-8", errors="replace")
    else:
        raise ValueError(f"不支持的文件格式: {ext}，支持: {', '.join(SUPPORTED_EXTENSIONS)}")


def _extract_pdf_text(file_bytes: bytes) -> str:
    """从PDF字节内容中提取文本"""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(file_bytes))
        texts = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
        if not texts:
            raise ValueError("PDF文件中没有提取到文本（可能是扫描件或图片PDF）")
        return "\n\n".join(texts)
    except ImportError:
        raise ImportError("需要安装 pypdf: pip install pypdf")
    except Exception as e:
        if "not extract" in str(e).lower() or "no text" in str(e).lower():
            raise ValueError("PDF文件中没有提取到文本（可能是扫描件或图片PDF）")
        raise ValueError(f"PDF解析失败: {str(e)}")


def get_file_info(filename: str, file_bytes: bytes) -> dict:
    """获取文件信息"""
    ext = os.path.splitext(filename)[1].lower()
    text = extract_text_from_file(filename, file_bytes)
    return {
        "filename": filename,
        "extension": ext,
        "size_bytes": len(file_bytes),
        "text_length": len(text),
        "text_preview": text[:200],
        "text": text,
    }

# ============================================
# 嵌入函数（中文优化）
# ============================================
# 使用 sentence-transformers 的轻量多语言模型
# paraphrase-multilingual-MiniLM-L12-v2 对中文支持好
# 也可以用 all-MiniLM-L6-v2（更轻量但中文略弱）
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# 全局单例
_embedding_fn = None
_chroma_client = None


def get_embedding_function():
    """获取嵌入函数（延迟加载，只加载一次）"""
    global _embedding_fn
    if _embedding_fn is None:
        from chromadb.utils import embedding_functions
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=EMBEDDING_MODEL,
            device="cpu",
        )
    return _embedding_fn


def get_chroma_client():
    """获取ChromaDB客户端（单例）"""
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=CHROMA_DIR,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
    return _chroma_client


# ============================================
# 文档分块器
# ============================================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,          # 每块500字
    chunk_overlap=100,       # 重叠100字，保证上下文连贯
    separators=["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""],
)


# ============================================
# KnowledgeBase 主类
# ============================================
class KnowledgeBase:
    """知识库管理器"""

    DEFAULT_COLLECTION = "ai_avatar_knowledge"

    def __init__(self, collection_name: str = None):
        self.collection_name = collection_name or self.DEFAULT_COLLECTION
        self.client = get_chroma_client()
        self.embedding_fn = get_embedding_function()
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """获取或创建集合"""
        try:
            return self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
            )
        except Exception:
            return self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_fn,
                metadata={"description": "AI数字分身知识库"},
            )

    # ==========================================
    # 添加文档
    # ==========================================
    def add_document(
        self,
        title: str,
        content: str,
        category: str = "通用",
        source: str = "手动录入",
    ) -> int:
        """
        添加文档到知识库

        参数:
            title: 文档标题
            content: 文档内容
            category: 分类标签（如"脚本模板"/"行业知识"/"个人素材"）
            source: 来源（文件名/URL等）

        返回:
            添加的chunk数量
        """
        # 分块
        chunks = text_splitter.split_text(content)
        if not chunks:
            return 0

        # 生成唯一ID前缀
        doc_hash = hashlib.md5(f"{title}{content[:100]}".encode()).hexdigest()[:8]
        now = datetime.now().isoformat()

        ids = []
        metadatas = []
        documents = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_hash}_{i}"
            ids.append(chunk_id)
            metadatas.append({
                "title": title,
                "category": category,
                "source": source,
                "chunk_index": i,
                "total_chunks": len(chunks),
                "added_at": now,
            })
            documents.append(chunk)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        return len(chunks)

    def add_file(
        self,
        filename: str,
        file_bytes: bytes,
        category: str = "通用",
    ) -> tuple[int, str]:
        """
        从上传文件中添加知识

        参数:
            filename: 原始文件名
            file_bytes: 文件字节内容
            category: 分类标签

        返回:
            (chunk数量, 提取的文本预览)
        """
        text = extract_text_from_file(filename, file_bytes)
        title = os.path.splitext(filename)[0]  # 去掉扩展名作为标题
        chunk_count = self.add_document(
            title=title,
            content=text,
            category=category,
            source=filename,
        )
        return chunk_count, text[:500]

    # ==========================================
    # 搜索文档
    # ==========================================
    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
    ) -> list[dict]:
        """
        搜索知识库

        参数:
            query: 搜索查询
            top_k: 返回结果数
            category: 可选，按分类过滤

        返回:
            搜索结果列表 [{"content": ..., "metadata": ..., "score": ...}, ...]
        """
        where_filter = None
        if category:
            where_filter = {"category": category}

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.count()),
            where=where_filter,
        )

        # 整理结果
        items = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                items.append({
                    "id": doc_id,
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "score": 1.0 - results["distances"][0][i] if results["distances"] else 0,
                })
        return items

    # ==========================================
    # 格式化上下文
    # ==========================================
    def format_context(self, results: list[dict], max_tokens: int = 2000) -> str:
        """
        将搜索结果格式化为可注入AI的上下文

        参数:
            results: search()返回的结果列表
            max_tokens: 最大token数（粗略按字数算）

        返回:
            格式化的上下文字符串
        """
        if not results:
            return ""

        lines = ["【知识库检索结果】", "以下是从你的知识库中找到的相关内容：", ""]
        char_count = 0

        for i, r in enumerate(results, 1):
            title = r["metadata"].get("title", "未知")
            category = r["metadata"].get("category", "")
            content = r["content"].strip()

            entry = f"### 参考{i}：{title}"
            if category:
                entry += f" [{category}]"
            entry += f"\n{content}\n"

            if char_count + len(entry) > max_tokens:
                break

            lines.append(entry)
            char_count += len(entry)

        lines.append("---")
        lines.append("请基于以上知识库内容，结合你的能力来回答用户的问题。")
        return "\n".join(lines)

    def search_and_format(
        self,
        query: str,
        top_k: int = 3,
        category: Optional[str] = None,
    ) -> str:
        """一站式搜索+格式化"""
        results = self.search(query, top_k=top_k, category=category)
        return self.format_context(results)

    # ==========================================
    # 管理功能
    # ==========================================
    def count(self) -> int:
        """文档总数"""
        return self.collection.count()

    def get_categories(self) -> list[str]:
        """获取所有分类"""
        try:
            results = self.collection.get()
            if results["metadatas"]:
                cats = set(m.get("category", "未分类") for m in results["metadatas"])
                return sorted(cats)
        except Exception:
            pass
        return []

    def get_document_list(self) -> list[dict]:
        """获取文档列表（按标题去重）"""
        try:
            results = self.collection.get()
            if not results["metadatas"]:
                return []

            seen = set()
            docs = []
            for meta in results["metadatas"]:
                title = meta.get("title", "未知")
                if title not in seen:
                    seen.add(title)
                    docs.append({
                        "title": title,
                        "category": meta.get("category", ""),
                        "source": meta.get("source", ""),
                        "chunks": sum(1 for m in results["metadatas"] if m.get("title") == title),
                        "added_at": meta.get("added_at", ""),
                    })
            return docs
        except Exception:
            return []

    def delete_document(self, title: str) -> int:
        """按标题删除文档，返回删除的chunk数"""
        try:
            results = self.collection.get()
            ids_to_delete = []
            for i, meta in enumerate(results["metadatas"]):
                if meta.get("title") == title:
                    ids_to_delete.append(results["ids"][i])

            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
            return len(ids_to_delete)
        except Exception as e:
            return 0

    def get_stats(self) -> dict:
        """获取知识库统计信息"""
        try:
            cats = self.get_categories()
            docs = self.get_document_list()
            return {
                "total_chunks": self.count(),
                "total_docs": len(docs),
                "categories": cats,
                "docs": docs,
            }
        except Exception:
            return {
                "total_chunks": 0,
                "total_docs": 0,
                "categories": [],
                "docs": [],
            }

    def wipe(self):
        """清空知识库（危险操作）"""
        try:
            # 获取所有文档ID并逐个删除
            results = self.collection.get()
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
        except Exception:
            pass
        # 删除并重建集合
        try:
            self.client.delete_collection(self.COLLECTION_NAME)
        except Exception:
            pass
        self.collection = self._get_or_create_collection()


# ============================================
# 全局单例
# ============================================
_kb_instance: Optional[KnowledgeBase] = None


def get_kb() -> KnowledgeBase:
    """获取知识库全局单例"""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance


# ============================================
# 示例种子数据（首次使用自动导入）
# ============================================
SEED_DOCUMENTS = [
    {
        "title": "📖 黄金Hook开头公式",
        "category": "脚本模板",
        "content": """
短视频黄金Hook开头公式：

1. 悬念型："你绝对想不到..."、"99%的人不知道..."
2. 反常识型："月薪3000比月薪3万更快乐？"
3. 痛点型："你是不是也经常..."、"每次...都很崩溃"
4. 数字型："3个方法"、"第4个绝了"、"5天涨粉10万"
5. 对比型："以前vs现在"、"普通人vs博主"
6. 情绪型："太爽了！"、"泪目了..."、"谁懂啊！"
7. 共鸣型："这说的不就是我吗"、"终于有人说了"

使用原则：
- 前3秒必须说完Hook
- Hook要跟目标受众直接相关
- 一个视频只用一种Hook类型
- 测试不同Hook看数据反馈
""",
    },
    {
        "title": "📊 抖音算法机制要点",
        "category": "行业知识",
        "content": """
抖音推荐算法核心机制（2025版）：

1. 流量池递进：
   初始流量池：200-500播放 → 看完播率和互动
   千人池：1000-5000播放 → 看转粉率和分享
   万人池：1万-10万 → 看评论质量和完播
   热门池：100万+ → 看社会价值和话题性

2. 关键指标权重（按重要性排序）：
   - 完播率（最重要！前3秒完播率最关键）
   - 互动率（点赞+评论+收藏+分享）
   - 转粉率（看了你的人有多少关注你）
   - 举报率（越低越好）

3. 发布时间建议：
   - 工作日：12:00-13:00、18:00-19:00、21:00-22:00
   - 周末：11:00-12:00、17:00-18:00、20:00-21:00
   - 垂直领域根据受众习惯微调

4. 内容冷启动：
   - 视频发布后1小时是黄金期
   - 冷启动数据好会继续推流
   - 前100个播放中互动率>5%为佳
""",
    },
    {
        "title": "✍️ 小红书爆款文案结构",
        "category": "脚本模板",
        "content": """
小红书爆款文案结构（4段式）：

【标题】= 关键词 + 痛点/好奇心 + 结果
示例："建议所有女生都去学这个技能！我用了3个月，工资翻倍"

【开头】= 共情 + 引子
"姐妹们，今天聊一个扎心的话题..."
"这篇笔记我纠结了很久要不要发..."

【正文】= 干货 + 个人经验
- 每段控制在2-3行
- 多用emoji分隔
- 穿插个人故事增加可信度
- 数据要具体（"1个月"比"很快"好）

【结尾】= 总结 + 互动引导
"总结一下就是这3点：①②③"
"你们遇到过这种情况吗？评论区聊聊"
"收藏这篇，下次找不到了！"

排版技巧：
- 每段之间空一行
- 用emoji做列表标记
- 关键词加粗或单独成行
- 文末加上关联话题标签
""",
    },
    {
        "title": "🎯 B站内容创作要点",
        "category": "行业知识",
        "content": """
B站内容创作核心要点：

1. B站用户特点：
   - 平均年龄22-28岁
   - 更看重内容深度和真诚度
   - 弹幕文化独特
   - 对广告比较敏感

2. 受欢迎的B站内容类型：
   - 深度测评（＞10分钟）
   - "速通"类教程（精炼干货）
   - 挑战/Vlog（真实记录）
   - 吐槽/点评（需要独到见解）

3. 标题技巧：
   - 用梗但不烂俗
   - 可以稍长（15-25字）
   - "数码区UP主不会告诉你的事"
   - "花3天整理的XX攻略，建议收藏"

4. 投币/收藏/点赞比例：
   - B站的收藏和投币比点赞更有价值
   - 干货类内容收藏率高
   - 收藏>5%就是优质内容
""",
    },
    {
        "title": "🎬 口播类短视频结构模板",
        "category": "脚本模板",
        "content": """
口播类短视频标准结构（60秒版）：

【0-3秒】Hook开头
- 痛点提问："你是不是也遇到过这种情况？"
- 反常识："其实XX根本不是你想的那样"
- 结果展示："我用这个方法3天涨了1万粉"

【3-10秒】背景铺垫
- 一句话交代背景
- 建立共鸣："我以前也以为..."
- 制造期待："直到我发现了一个秘密"

【10-45秒】干货正文（核心）
- 3个要点，每个10-15秒
- 要点之间用"第一/第二/第三"或"首先/其次/最后"串联
- 每个要点：观点1句 + 解释1句 + 例子1句
- 多用"你"字，制造对话感

【45-55秒】总结升华
- "总结一下就是..." 1-2句话
- 给受众一个认知升级

【55-60秒】互动引导
- "你觉得呢？评论区告诉我"
- "下一期想看什么？"
- "关注我，每天分享运营干货"
""",
    },
    {
        "title": "📱 视频号内容运营策略",
        "category": "行业知识",
        "content": """
视频号运营核心策略（2025-2026版）：

1. 视频号与抖音的核心差异：
   - 分发机制：社交推荐（朋友点赞）+ 算法推荐，双引擎
   - 用户画像：25-45岁为主，比抖音更成熟
   - 内容偏好：知识类、情感类、生活类更受欢迎
   - 变现模式：直播+私域转化是核心

2. 适合视频号的内容类型：
   - 知识付费类内容（引流到私域）
   - 中长视频（3-10分钟）完播率更高
   - 真实故事类（素人视角，减少精致感）
   - 行业观察/趋势类

3. 视频号冷启动技巧：
   - 朋友圈首发（发动朋友点赞）
   - 微信群转发+红包引导互动
   - 绑定公众号互相引流
   - 直播涨粉效率最高（1小时直播≈10条视频涨粉量）

4. 发布时间建议：
   - 工作日：早7-9点（通勤）、晚20-22点（睡前）
   - 周末：早9-11点、晚20-23点
   - 视频号用户晚上活跃度更高
""",
    },
    {
        "title": "🏷️ 短视频标题优化技巧",
        "category": "脚本模板",
        "content": """
短视频爆款标题方法论：

1. 标题公式：
   【关键词】+ 【痛点/好奇】+ 【利益承诺】
   示例："【打工人必看】3个副业方法，月入5000不是梦"

2. 标题类型与示例：
   - 数字清单型："5个让你效率翻倍的AI工具"
   - 问题解答型："为什么你的视频总是不火？"
   - 结果展示型："用了这个方法，我7天涨粉2万"
   - 避坑警告型："新手做自媒体的3个致命错误"
   - 身份标签型："所有打工人，这条一定要看"
   - 时间紧迫型："再不看就删了！平台最新算法变化"

3. 标题优化技巧：
   - 前8个字最重要（feed流只展示前8-15字）
   - 用数字更吸睛（3个方法 > 几个方法）
   - 善用表情符号增加视觉冲击
   - A/B测试：同一条视频换2-3个标题发布
   - 抖音标题控制在15-25字最佳

4. 标题禁忌：
   - 不要标题党（完播率会崩）
   - 不要用"震惊""速看"等低质词（限流）
   - 不要全是大写/英文/生僻词
""",
    },
    {
        "title": "🎯 内容定位与人设打造",
        "category": "行业知识",
        "content": """
短视频人设打造指南：

1. 人设三要素：
   - 专业度：你懂什么？（知识/技能/经验）
   - 亲近感：你为什么值得信？（真实/接地气/共情）
   - 差异化：你和别人有什么不同？（独特视角/风格/经历）

2. 垂直领域定位法：
   第一步：列出你擅长的3个领域
   第二步：每个领域找10个头部账号分析
   第三步：找到「你能做但别人没做」的空隙
   第四步：用3个标签定义自己（如：AI+运营+副业）

3. 内容金字塔模型：
   - 10% 爆款内容（追热点、大话题，做流量）
   - 30% 干货内容（深度教程、专业知识，做口碑）
   - 60% 日常内容（行业观点、个人感悟，做人设）

4. 一致性原则：
   - 视觉一致：封面统一模板、字体/配色固定
   - 表达一致：固定口头禅、语气、节奏
   - 选题一致：只做垂直领域，不跑偏
   - 频率一致：固定更新节奏（日更/周3更）

5. 人设翻车警示：
   - 不要立完美人设（容易崩）
   - 不要碰敏感话题（政/宗/色）
   - 恰饭内容不超过20%（观众会反感）
""",
    },
    {
        "title": "📈 数据分析实操手册",
        "category": "行业知识",
        "content": """
短视频数据分析实操指南：

1. 必看核心指标：
   - 完播率：>30%及格，>50%优秀
     = 平均播放时长 / 视频总时长
   - 互动率：>3%及格，>8%优秀
     = (点赞+评论+收藏+分享) / 播放量
   - 转粉率：>1%优秀（每100个观看新增1个粉丝）
   - 前3秒完播率：>70%及格

2. 数据诊断流程：
   前3秒完播率低 → Hook不够吸引人，改开头
   中途流失严重 → 内容节奏有问题，中间太平淡
   结尾互动率低 → 没做互动引导，CTAs不够明确
   转粉率低 → 内容没让别人觉得"这人值得关注"

3. 每日复盘模板：
   - 今日发布X条
   - 总播放XXX, 环比昨天+/-X%
   - 最好的一条是(标题)，为什么好？
   - 最差的一条是(标题)，为什么差？
   - 明天尝试什么新方向？

4. 竞品分析技巧：
   - 每周分析3-5个同赛道账号
   - 重点看：选题方向、发布时间、互动话术
   - 用飞书/Notion建竞品库，定期更新
""",
    },
    {
        "title": "🤖 AI短视频创作工作流",
        "category": "脚本模板",
        "content": """
AI辅助短视频创作完整工作流：

1. 选题阶段（用AI）：
   - 输入你的领域 → AI推荐10个本周选题
   - 用热点分析工具看趋势
   - 选2-3个最优选题进入脚本阶段

2. 脚本阶段（AI生成+人工优化）：
   - AI生成初稿脚本
   - 人工修改：加真实案例、调语言风格、补金句
   - 朗读一遍：标记不顺口的句子
   - 80% AI + 20% 人工 = 最佳效果

3. 拍摄阶段（效率tips）：
   - 提词器APP（如轻抖），脚本导入自动滚动
   - 一次录3-5条，选最好的一条
   - 口播类：手机+补光灯+领夹麦就够

4. 后期阶段：
   - AI自动加字幕（剪映/度咔）
   - 封面用Canva模板（3分钟搞定）
   - BGM库提前建好（按情绪分类）

5. 发布阶段：
   - 选择最佳发布时间
   - 评论区先发一条引导评论
   - 发布后1小时内回复所有评论（算法加分）

6. 复盘阶段：
   - 24小时后看数据
   - 用AI数据分析工具诊断
   - 把爆款脚本存入知识库
""",
    },
]


def seed_knowledge_base():
    """首次使用时导入种子数据"""
    kb = get_kb()
    if kb.count() > 0:
        return  # 已有数据，跳过

    for doc in SEED_DOCUMENTS:
        kb.add_document(
            title=doc["title"],
            content=doc["content"],
            category=doc["category"],
            source="系统内置",
        )
    return len(SEED_DOCUMENTS)
