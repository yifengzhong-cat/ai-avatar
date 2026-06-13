"""
AI数字分身 - 热点追踪分析器
挖掘热点话题，给出内容创作结合点
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.utils.config import config
from app.utils.prompts import TREND_ANALYZER_PROMPT


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """获取LLM实例"""
    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        temperature=temperature,
    )


def analyze_trend(
    trend_topic: str,
    trend_data: str = "",
    time_context: str = "",
) -> str:
    """
    分析热点话题并给创作建议

    参数:
        trend_topic: 热点话题描述
        trend_data: 相关热度数据（播放量、参与人数等，可选）
        time_context: 时间上下文

    返回:
        热点分析报告（Markdown格式）
    """
    llm = get_llm(temperature=0.7)

    user_prompt = TREND_ANALYZER_PROMPT.format(
        trend_topic=trend_topic,
        niche=config.MY_NICHE,
        trend_data=trend_data or "请基于你的知识做分析",
    )
    if time_context:
        user_prompt += f"\n\n【时间参考】{time_context}"

    messages = [
        SystemMessage(content="你是一位短视频热点分析专家，输出使用Markdown格式。"),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return response.content


def suggest_topics(niche: str = "", count: int = 10, time_context: str = "") -> str:
    """
    基于领域推荐选题

    参数:
        niche: 垂直领域
        count: 选题数量

    返回:
        选题列表
    """
    llm = get_llm(temperature=0.9)
    niche = niche or config.MY_NICHE

    prompt = f"""你是一个短视频选题策划专家。请为「{niche}」领域推荐{count}个本周值得做的选题。

要求：
1. 选题要有爆款潜力
2. 结合用户需求痛点
3. 每个选题标注难度（⭐~⭐⭐⭐⭐⭐）和预估播放量级

格式：
| # | 选题方向 | 选题类型 | 难度 | 预估播放 | 一句话Hook |
|---|---------|---------|------|---------|-----------|
| 1 | ... | ... | ⭐⭐⭐ | 10w+ | ... |"""
    if time_context:
        prompt += f"\n\n{time_context}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def daily_hotspots(time_context: str = "") -> str:
    """
    获取近期平台热门趋势（基于AI知识）

    返回:
        热门趋势汇总
    """
    llm = get_llm(temperature=0.5)

    prompt = f"""请列出当前抖音/小红书/视频号平台的最新热门趋势。

包括：
1. 热门BGM/音乐
2. 热门挑战/话题标签
3. 内容形式新趋势（如AI生成内容、互动视频等）
4. 平台政策/算法变化

针对每个趋势，说明{config.MY_NICHE}领域的创作者可以如何借势。"""
    if time_context:
        prompt += f"\n\n【时间参考】{time_context}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
