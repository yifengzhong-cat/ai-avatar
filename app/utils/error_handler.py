"""
AI数字分身 - 统一错误处理
让API报错不再是吓人的红字，而是友好的中文提示
"""
import time
import streamlit as st
from functools import wraps
from typing import Callable, Any


# ============================================
# 错误类型 → 用户友好提示
# ============================================
ERROR_MESSAGES = {
    "rate_limit": "🚦 API调用太频繁了，请等几秒再试～",
    "timeout": "⏰ AI响应超时，可能网络不太好，再试一次？",
    "auth": "🔑 API Key 好像有问题，检查一下配置？",
    "insufficient_quota": "💰 API 余额不足了，去 DeepSeek 后台充个值吧～",
    "content_filter": "🚫 内容被安全过滤了，换个表述试试？",
    "connection": "🌐 网络连接失败，检查网络或API地址配置",
    "server_error": "🖥️ AI服务暂时故障，等几秒再试～",
    "unknown": "😅 出了点意外错误，再试一次吧。不行就截图找开发者～",
}


def classify_error(error: Exception) -> str:
    """根据异常信息分类错误类型"""
    msg = str(error).lower()

    if "rate" in msg or "too many" in msg:
        return "rate_limit"
    elif "timeout" in msg or "timed out" in msg:
        return "timeout"
    elif "auth" in msg or "unauthorized" in msg or "invalid api key" in msg:
        return "auth"
    elif "quota" in msg or "insufficient" in msg or "billing" in msg:
        return "insufficient_quota"
    elif "content" in msg and "filter" in msg or "safety" in msg:
        return "content_filter"
    elif "connection" in msg or "network" in msg or "refused" in msg:
        return "connection"
    elif "500" in msg or "server" in msg or "internal" in msg:
        return "server_error"
    else:
        return "unknown"


def get_user_message(error_type: str, extra: str = "") -> str:
    """获取用户友好的错误提示"""
    base = ERROR_MESSAGES.get(error_type, ERROR_MESSAGES["unknown"])
    if extra:
        base += f"\n\n<small>技术细节：{extra[:200]}</small>"
    return base


# ============================================
# 重试装饰器
# ============================================
def with_retry(max_retries: int = 2, base_delay: float = 1.5):
    """
    API调用的自动重试装饰器
    只重试可恢复的错误（超时、限流、服务器错误）
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    error_type = classify_error(e)

                    # 不可重试的错误直接抛出
                    if error_type in ("auth", "insufficient_quota", "content_filter"):
                        raise

                    # 最后一次尝试也失败了
                    if attempt == max_retries:
                        raise

                    # 等待后重试
                    delay = base_delay * (2 ** attempt)
                    time.sleep(delay)
            raise last_error
        return wrapper
    return decorator


# ============================================
# Streamlit 安全执行
# ============================================
def safe_ai_call(func: Callable, *args, **kwargs):
    """
    安全调用AI函数，自动处理异常并显示友好提示

    用法:
        result = safe_ai_call(generate_script, topic="xxx", ...)
        if result is None:
            return  # 错误已显示
        # 正常使用result
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_type = classify_error(e)
        msg = get_user_message(error_type, str(e))

        st.error(msg)

        # 给出具体操作建议
        if error_type == "auth":
            st.info("💡 去 [DeepSeek](https://platform.deepseek.com/) 重新生成一个Key")
        elif error_type == "insufficient_quota":
            st.info("💡 去 [DeepSeek充值页面](https://platform.deepseek.com/top_up) 充值，¥1就够用很久")
        elif error_type in ("rate_limit", "timeout", "server_error"):
            if st.button("🔄 重试", use_container_width=True):
                st.rerun()

        return None


# ============================================
# 流式安全执行（含进度提示）
# ============================================
def safe_stream_call(status_msg: str = "AI思考中..."):
    """
    用作上下文管理器，包裹流式调用
    自动处理异常

    用法:
        with safe_stream_call("正在生成脚本..."):
            for chunk in llm.stream(...):
                yield chunk
    """
    class StreamContext:
        def __enter__(self):
            self.spinner = st.spinner(status_msg)
            self.spinner.__enter__()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.spinner.__exit__(exc_type, exc_val, exc_tb)
            if exc_type is not None:
                error_type = classify_error(exc_val)
                msg = get_user_message(error_type, str(exc_val))
                st.error(msg)
                return True  # 抑制异常
            return False

    return StreamContext()
