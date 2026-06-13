"""
AI数字分身 - 内容数据分析助手
分析视频数据，给出优化建议
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from app.utils.config import config
from app.utils.prompts import DATA_ANALYZER_PROMPT


def get_llm(temperature: float = 0.3) -> ChatOpenAI:
    """数据分析用低温度，保证稳定输出"""
    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        temperature=temperature,
    )


def analyze_video_performance(video_data: str, time_context: str = "") -> str:
    """
    分析单条视频表现

    参数:
        video_data: 视频数据描述（播放量、点赞、评论、分享、完播率等）
        time_context: 时间上下文

    返回:
        分析报告
    """
    llm = get_llm(temperature=0.3)

    user_prompt = DATA_ANALYZER_PROMPT.format(video_data=video_data)
    if time_context:
        user_prompt += f"\n\n【时间参考】{time_context}"
    response = llm.invoke([HumanMessage(content=user_prompt)])
    return response.content


def quick_diagnose(
    views: int,
    likes: int,
    comments: int,
    shares: int,
    followers_gain: int,
    play_duration: float,
    video_duration: float,
    time_context: str = "",
) -> str:
    """
    快速诊断视频数据

    参数:
        views: 播放量
        likes: 点赞
        comments: 评论
        shares: 分享
        followers_gain: 涨粉
        play_duration: 平均播放时长（秒）
        video_duration: 视频总时长（秒）
    """
    llm = get_llm(temperature=0.3)

    # 计算关键指标
    like_rate = (likes / views * 100) if views > 0 else 0
    comment_rate = (comments / views * 100) if views > 0 else 0
    share_rate = (shares / views * 100) if views > 0 else 0
    completion_rate = (play_duration / video_duration * 100) if video_duration > 0 else 0

    data_text = f"""
- 播放量: {views:,}
- 点赞: {likes:,} (点赞率 {like_rate:.2f}%)
- 评论: {comments:,} (评论率 {comment_rate:.2f}%)
- 分享: {shares:,} (分享率 {share_rate:.2f}%)
- 涨粉: {followers_gain:,}
- 平均播放时长: {play_duration:.1f}秒
- 视频总时长: {video_duration:.1f}秒
- 完播率: {completion_rate:.1f}%
"""

    prompt = f"""快速诊断以下短视频数据，用表格形式输出。

{data_text}

格式要求：
1. 一个诊断表格（指标|数值|评级|说明）
2. 3条具体优化建议（按优先级排序）
3. 一句话总结"""

    if time_context:
        prompt += f"\n\n【时间参考】{time_context}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def content_calendar_suggestion(account_type: str = "", time_context: str = "") -> str:
    """
    提供内容排期建议

    参数:
        account_type: 账号类型
    """
    llm = get_llm(temperature=0.7)
    account_type = account_type or config.MY_NICHE

    prompt = f"""为一个「{account_type}」类型的短视频账号规划一周内容排期。

要求：
1. 周一到周日，每天1-2条内容
2. 每条标注：选题方向、内容类型、预估制作时长、发布时段
3. 考虑周末流量特点
4. 给出B-roll/素材复用建议

用表格形式输出。"""

    if time_context:
        prompt += f"\n\n【时间参考】{time_context}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
