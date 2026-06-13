"""
AI数字分身 - 实时时间工具
每次调用都动态获取当前时间，不缓存
"""
from datetime import datetime, timezone, timedelta


# 中国时区
CN_TZ = timezone(timedelta(hours=8))


def get_now():
    """获取当前时间（中国时区），每次调用都重新计算"""
    return datetime.now(CN_TZ)


def get_date_cn() -> str:
    """获取中文日期字符串，每次调用实时计算"""
    now = get_now()
    weekdays = ["一", "二", "三", "四", "五", "六", "日"]
    return f"{now.year}年{now.month}月{now.day}日（星期{weekdays[now.weekday()]}）"


def get_time_ctx() -> str:
    """获取完整时间上下文，直接注入到AI提示词中"""
    now = get_now()
    date_cn = get_date_cn()
    return (
        f"【重要时间参考】现在是{date_cn}，"
        f"北京时间{now.hour:02d}:{now.minute:02d}。"
        f"请基于这个时间点来思考和分析，确保内容时效性正确。"
    )


def get_week_range() -> str:
    """获取本周日期范围"""
    now = get_now()
    weekday = now.weekday()
    monday = now - timedelta(days=weekday)
    sunday = monday + timedelta(days=6)
    return f"{monday.month}月{monday.day}日 - {sunday.month}月{sunday.day}日"


def get_time_display() -> str:
    """获取用于UI显示的当前时间"""
    now = get_now()
    return now.strftime("%Y-%m-%d %H:%M:%S")
