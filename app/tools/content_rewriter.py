"""
AI数字分身 - 多平台内容改写器
将内容适配到不同平台的风格
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.utils.config import config
from app.utils.prompts import CONTENT_REWRITER_PROMPT, COMMENT_REPLY_PROMPT


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """获取LLM实例"""
    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        temperature=temperature,
    )


def rewrite_for_platform(
    original_content: str,
    target_platform: str,
    source_platform: str = "通用",
    time_context: str = "",
) -> str:
    """
    将内容改写适配到目标平台

    参数:
        original_content: 原始内容
        target_platform: 目标平台（抖音/小红书/视频号/B站）
        source_platform: 原始平台
        time_context: 时间上下文

    返回:
        改写后的内容
    """
    llm = get_llm(temperature=0.7)

    user_prompt = CONTENT_REWRITER_PROMPT.format(
        target_platform=target_platform,
        original_content=original_content,
        source_platform=source_platform,
    )
    if time_context:
        user_prompt += f"\n\n【时间参考】{time_context}"

    response = llm.invoke([HumanMessage(content=user_prompt)])
    return response.content


def generate_title_variations(content: str, platform: str = "抖音", count: int = 5, time_context: str = "") -> str:
    """为内容生成多个标题变体"""
    llm = get_llm(temperature=0.9)

    prompt = f"""基于以下内容，为{platform}平台生成{count}个吸引人的标题。

内容摘要：{content[:500]}

要求：
- 每个标题不超过30字
- 涵盖：悬念型、数字型、痛点型、反常识型、情绪型
- 直接输出编号列表"""
    if time_context:
        prompt += f"\n\n{time_context}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def reply_to_comment(comment: str, time_context: str = "") -> str:
    """模拟博主回复粉丝评论"""
    llm = get_llm(temperature=0.8)

    prompt = COMMENT_REPLY_PROMPT.format(
        my_name=config.MY_NAME,
        my_style=config.MY_STYLE,
        comment=comment,
    )
    if time_context:
        prompt += f"\n\n{time_context}"

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
