"""
AI数字分身 - 脚本质量评分器
从多维度评估脚本质量，给出改进建议

评分维度：
- Hook力：开头3秒抓人程度
- 结构力：逻辑清晰、节奏好
- 传播力：转发/分享潜力
- 完播预测：观众看完的概率
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.utils.config import config


SCORER_PROMPT = """你是一位顶级短视频内容评审官，擅长从数据维度评估脚本质量。

【任务】评估以下短视频脚本，从4个维度打分（满分10分），并给出改进建议。

【脚本内容】
{script_content}

【视频信息】
- 平台：{platform}
- 类型：{video_type}
- 目标时长：{duration}秒
- 目标受众：{audience}

【评分维度】
1. 🎣 Hook力（0-10分）：开头3秒能否抓住观众？是否有悬念/痛点/反常识？
2. 🏗️ 结构力（0-10分）：脚本逻辑是否清晰？节奏是否紧凑？有无废话？
3. 📡 传播力（0-10分）：观众愿不愿意转发/分享？有没有金句/情绪爆点？
4. ⏱️ 完播预测（0-10分）：观众有多大可能看完？是否有中途流失风险？

【输出格式】
直接输出Markdown表格：

| 维度 | 评分 | 点评 |
|------|------|------|
| 🎣 Hook力 | X/10 | 一句话点评 |
| 🏗️ 结构力 | X/10 | 一句话点评 |
| 📡 传播力 | X/10 | 一句话点评 |
| ⏱️ 完播预测 | X/10 | 一句话点评 |

**综合评分：XX/40** （一句话总结）

**🔧 3条改进建议：**
1. [具体操作]
2. [具体操作]
3. [具体操作]

**💎 如果只改一处：** [最关键的优化点]
"""


def get_llm(temperature: float = 0.3):
    return ChatOpenAI(
        model=config.LLM_MODEL,
        api_key=config.OPENAI_API_KEY,
        base_url=config.OPENAI_BASE_URL,
        temperature=temperature,
    )


def score_script(
    script_content: str,
    platform: str = "抖音",
    video_type: str = "口播",
    duration: int = 60,
    audience: str = "普通用户",
) -> str:
    """
    对脚本进行AI质量评分

    参数:
        script_content: 脚本全文
        platform: 目标平台
        video_type: 视频类型
        duration: 时长
        audience: 目标受众

    返回:
        评分报告（Markdown）
    """
    llm = get_llm(temperature=0.3)

    prompt = SCORER_PROMPT.format(
        script_content=script_content[:3000],  # 截断过长内容
        platform=platform,
        video_type=video_type,
        duration=duration,
        audience=audience,
    )

    messages = [
        SystemMessage(content="你是一位短视频质量评审专家，输出使用Markdown。"),
        HumanMessage(content=prompt),
    ]

    response = llm.invoke(messages)
    return response.content


def refine_script_section(
    original_script: str,
    section_description: str,
    instruction: str,
) -> str:
    """
    对话式精修：只改脚本的某一部分

    参数:
        original_script: 原始脚本全文
        section_description: 要修改的部分描述（如"第二段口播文案"）
        instruction: 修改指令（如"改得更口语化"）

    返回:
        精修后的完整脚本
    """
    llm = get_llm(temperature=0.7)

    prompt = f"""你是一位短视频脚本编辑。

【原始脚本】
{original_script}

【修改范围】只修改「{section_description}」这部分

【修改要求】{instruction}

【输出要求】
1. 输出完整的修改后脚本（不是只输出修改的部分）
2. 在修改过的地方用 **粗体** 标记
3. 脚本末尾附一个简短的「修改说明」"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content


def suggest_improvements(script_content: str, aspect: str = "hook") -> str:
    """
    针对某一维度快速给改进建议

    参数:
        script_content: 脚本内容
        aspect: 要优化的维度（hook/structure/viral/retention）

    返回:
        改进建议
    """
    llm = get_llm(temperature=0.8)

    aspect_map = {
        "hook": "开头Hook的吸引力",
        "structure": "脚本结构和节奏",
        "viral": "传播力和金句",
        "retention": "完播率和留存",
    }

    prompt = f"""针对以下脚本的「{aspect_map.get(aspect, aspect)}」，给出3条快速改进建议：

{script_content[:1500]}

要求：每条建议不超过30字，直接输出编号列表。"""

    response = llm.invoke([HumanMessage(content=prompt)])
    return response.content
