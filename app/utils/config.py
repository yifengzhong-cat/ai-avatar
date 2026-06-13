"""
AI数字分身 - 配置管理
支持本地 .env 和 Streamlit Cloud Secrets 两种模式
"""
import os
import streamlit as st
from dotenv import load_dotenv

# 加载 .env 文件（本地开发用，云端无此文件会自动跳过）
load_dotenv()


def _get_secret(key: str, default: str = "") -> str:
    """
    统一的配置读取方式
    优先级：Streamlit Cloud Secrets > .env 环境变量 > 默认值
    """
    # 先尝试从 Streamlit Cloud Secrets 读取
    try:
        # st.secrets 在云端是 dict，本地是 Secrets 对象
        value = st.secrets.get(key, None)
        if value:
            return str(value)
    except Exception:
        pass

    # 再尝试从环境变量读取（.env）
    return os.getenv(key, default)


class Config:
    """全局配置"""

    # LLM配置
    @property
    def OPENAI_API_KEY(self) -> str:
        return _get_secret("OPENAI_API_KEY", "")

    @property
    def OPENAI_BASE_URL(self) -> str:
        return _get_secret("OPENAI_BASE_URL", "https://api.openai.com/v1")

    @property
    def LLM_MODEL(self) -> str:
        return _get_secret("LLM_MODEL", "gpt-4o-mini")

    # 个人设定
    @property
    def MY_NAME(self) -> str:
        return _get_secret("MY_NAME", "运营小能手")

    @property
    def MY_NICHE(self) -> str:
        return _get_secret("MY_NICHE", "短视频运营")

    @property
    def MY_STYLE(self) -> str:
        return _get_secret("MY_STYLE", "幽默接地气，擅长用生活化比喻")

    # 访问密码（给朋友用的时候设置）
    @property
    def APP_PASSWORD(self) -> str:
        return _get_secret("APP_PASSWORD", "aigod123")

    def validate(self) -> bool:
        """验证配置是否完整"""
        key = self.OPENAI_API_KEY
        if not key or key == "sk-your-api-key-here":
            return False
        return True

    def get_status(self) -> dict:
        """获取配置状态"""
        return {
            "api_ready": self.validate(),
            "model": self.LLM_MODEL,
            "name": self.MY_NAME,
            "niche": self.MY_NICHE,
            "style": self.MY_STYLE,
        }


config = Config()
