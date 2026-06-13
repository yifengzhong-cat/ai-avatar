"""
AI数字分身 - 短视频脚本生成器
支持多种视频类型的脚本创作
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.utils.config import config
from app.utils.prompts import SCRIPT_WRITER_PROMPT, PERSONA_SYSTEM_PROMPT


def get_llm(temperature: float = 0.8) -> ChatOpenAI:
    """获取LLM实例"""
    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        temperature=temperature,
    )


def generate_script(
    topic: str,
    video_type: str = "口播",
    target_audience: str = "普通用户",
    duration: int = 60,
    key_message: str = "",
    trend_context: str = "无特殊热点",
    platform: str = "抖音",
    time_context: str = "",
) -> str:
    """
    生成短视频脚本

    参数:
        topic: 视频主题
        video_type: 视频类型（口播/剧情/Vlog/测评/干货教程/产品种草）
        target_audience: 目标受众
        duration: 视频时长（秒）
        key_message: 核心卖点/金句
        trend_context: 参考热点
        platform: 目标平台
        time_context: 时间上下文（如"现在是2026年6月13日"）

    返回:
        完整的脚本内容（Markdown格式）
    """
    llm = get_llm(temperature=0.8)

    # 构建提示词
    persona = PERSONA_SYSTEM_PROMPT.format(
        my_name=config.MY_NAME,
        my_niche=config.MY_NICHE,
        my_style=config.MY_STYLE,
    )
    if time_context:
        persona += f"\n\n【重要】{time_context}"

    user_prompt = SCRIPT_WRITER_PROMPT.format(
        platform=platform,
        topic=topic,
        video_type=video_type,
        target_audience=target_audience,
        duration=duration,
        key_message=key_message or "请根据主题自行提炼",
        trend_context=trend_context,
    )

    messages = [
        SystemMessage(content=persona),
        HumanMessage(content=user_prompt),
    ]

    response = llm.invoke(messages)
    return response.content


def generate_hooks(topic: str, count: int = 5, time_context: str = "") -> str:
    """快速生成视频Hook开头"""
    llm = get_llm(temperature=0.9)

    prompt = f"""你是短视频Hook大师。为主题「{topic}」生成{count}个抓人的开头Hook。

要求：
- 每个Hook不超过15个字
- 类型多样：悬念型、反常识型、痛点型、数字型、对比型
- 适合抖音/小红书平台

直接输出编号列表，不要多余解释。"""
    if time_context:
        prompt += f"\n\n{time_context}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
