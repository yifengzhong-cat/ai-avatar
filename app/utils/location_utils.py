"""
AI数字分身 - 实时定位模块
双层定位：浏览器GPS（高精度） + IP定位（兜底）

提供：
- 城市/省份/国家
- 经纬度
- 时区
- 本地化AI上下文
"""
import json
import time
from datetime import timezone, timedelta
from typing import Optional

import requests
import streamlit as st
import streamlit.components.v1 as components


# ============================================
# 定位数据结构
# ============================================
class Location:
    """定位信息"""
    def __init__(self, data: dict, source: str = "unknown"):
        self.source = source  # "gps" | "ip" | "manual"
        self.city: str = data.get("city", "")
        self.region: str = data.get("region", data.get("region_code", ""))
        self.country: str = data.get("country_name", data.get("country", ""))
        self.latitude: float = float(data.get("latitude", 0))
        self.longitude: float = float(data.get("longitude", 0))
        self.timezone_name: str = data.get("timezone", "Asia/Shanghai")
        self.utc_offset: str = data.get("utc_offset", "+0800")

    @property
    def display_name(self) -> str:
        """显示用名称"""
        parts = []
        if self.country:
            parts.append(self.country)
        if self.region:
            parts.append(self.region)
        if self.city:
            parts.append(self.city)
        return " · ".join(parts) if parts else "未知位置"

    @property
    def short_name(self) -> str:
        """简短名称"""
        if self.city:
            return self.city
        if self.region:
            return self.region
        return "未知"

    @property
    def timezone(self):
        """获取时区对象"""
        try:
            hours_str = self.utc_offset.replace("+", "").replace("-", "")
            hours = int(hours_str[:2]) if len(hours_str) >= 2 else 8
            minutes = int(hours_str[2:]) if len(hours_str) >= 4 else 0
            if "-" in self.utc_offset:
                hours = -hours
                minutes = -minutes
            return timezone(timedelta(hours=hours, minutes=minutes))
        except Exception:
            return timezone(timedelta(hours=8))

    def to_ai_context(self) -> str:
        """转换为可注入AI的上下文字符串"""
        parts = [f"用户当前位置：{self.display_name}"]
        if self.latitude and self.longitude:
            parts.append(f"（经纬度: {self.latitude:.2f}, {self.longitude:.2f}）")
        parts.append(f"时区：{self.timezone_name} (UTC{self.utc_offset})")
        parts.append("")
        parts.append("请根据用户所在地区，提供更具本地化特色的内容建议。")
        parts.append(f"例如：结合{self.city or self.region or '当地'}的热门话题、方言习惯、地区文化等特点。")
        return "\n".join(parts)


# ============================================
# IP定位（兜底方案，无需权限）
# ============================================
def get_location_by_ip() -> Optional[Location]:
    """
    通过IP地址获取位置
    使用 ipapi.co 免费API（每天1000次免费）
    """
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("error"):
                return None
            return Location(data, source="ip")
    except Exception:
        pass

    # 备用：ip-api.com
    try:
        resp = requests.get("http://ip-api.com/json/", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                return Location({
                    "city": data.get("city", ""),
                    "region": data.get("regionName", ""),
                    "country_name": data.get("country", ""),
                    "latitude": data.get("lat", 0),
                    "longitude": data.get("lon", 0),
                    "timezone": data.get("timezone", "Asia/Shanghai"),
                    "utc_offset": "+0800",
                }, source="ip")
    except Exception:
        pass

    return None


# ============================================
# GPS定位（浏览器高精度，需用户授权）
# ============================================
def get_location_by_gps() -> Optional[Location]:
    """
    通过浏览器GPS获取位置
    使用JS获取，存到session_state
    """
    # 先检查session中是否已有GPS数据
    try:
        if "gps_location" in st.session_state and st.session_state.gps_location:
            data = st.session_state.gps_location
            if "timezone" not in data:
                data["timezone"] = "Asia/Shanghai"
                data["utc_offset"] = "+0800"
            return Location(data, source="gps")
    except Exception:
        pass

    return None


def request_gps_permission():
    """
    在页面上渲染一个隐藏的JS组件来请求GPS权限
    只在geo_location未获取过时才执行
    """
    if "gps_requested" in st.session_state and st.session_state.gps_requested:
        return

    # 标记已请求，避免重复
    st.session_state.gps_requested = True

    # JS组件：请求GPS权限并存储到localStorage
    js_code = """
    <script>
    (function() {
        // 避免重复请求
        if (window.__gpsRequested) return;
        window.__gpsRequested = true;

        if (!navigator.geolocation) return;

        navigator.geolocation.getCurrentPosition(
            function(pos) {
                const data = {
                    latitude: pos.coords.latitude,
                    longitude: pos.coords.longitude,
                    accuracy: pos.coords.accuracy,
                    timestamp: Date.now()
                };
                // 存到localStorage，页面刷新后读取
                localStorage.setItem('ai_avatar_gps', JSON.stringify(data));

                // 尝试通过Streamlit的postMessage通信
                if (window.parent) {
                    window.parent.postMessage({
                        isStreamlitMessage: true,
                        type: 'streamlit:setComponentValue',
                        value: JSON.stringify(data)
                    }, '*');
                }

                // 反向地理编码获取城市名
                fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${pos.coords.latitude}&lon=${pos.coords.longitude}&zoom=10&accept-language=zh`)
                    .then(r => r.json())
                    .then(geo => {
                        const city = geo.address.city || geo.address.town || geo.address.county || '';
                        const region = geo.address.state || geo.address.province || '';
                        const country = geo.address.country || '';
                        const enriched = {
                            ...data,
                            city: city,
                            region: region,
                            country_name: country,
                            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || 'Asia/Shanghai',
                            utc_offset: '+0' + (-new Date().getTimezoneOffset() / 60).toFixed(0) + '00'
                        };
                        localStorage.setItem('ai_avatar_gps', JSON.stringify(enriched));
                    })
                    .catch(() => {});
            },
            function(err) {
                console.log('GPS denied or unavailable:', err.message);
                localStorage.setItem('ai_avatar_gps_denied', 'true');
            },
            { enableHighAccuracy: false, timeout: 8000, maximumAge: 600000 }
        );
    })();
    </script>
    """
    components.html(js_code, height=0)


def read_gps_from_storage():
    """
    从localStorage读取GPS数据（通过一个桥接组件）
    """
    if "gps_loaded" in st.session_state and st.session_state.gps_loaded:
        return

    bridge = """
    <script>
    const gpsData = localStorage.getItem('ai_avatar_gps');
    const denied = localStorage.getItem('ai_avatar_gps_denied');
    const msg = {
        isStreamlitMessage: true,
        type: 'streamlit:setComponentValue',
        value: JSON.stringify({gps: gpsData ? JSON.parse(gpsData) : null, denied: !!denied})
    };
    window.parent.postMessage(msg, '*');
    </script>
    """
    components.html(bridge, height=0)
    st.session_state.gps_loaded = True


# ============================================
# 统一获取定位（GPS优先，IP兜底）
# ============================================
def get_location(force_refresh: bool = False) -> Location:
    """
    获取当前定位
    优先级：GPS > IP > 默认值

    参数:
        force_refresh: 强制重新检测

    返回:
        Location对象
    """
    # 检查缓存（兼容非Streamlit环境）
    try:
        if not force_refresh and "cached_location" in st.session_state:
            cached = st.session_state.cached_location
            if time.time() - cached["ts"] < 300:
                return cached["location"]
    except Exception:
        pass  # 非Streamlit环境，跳过缓存

    location = None

    # 辅助：安全缓存
    def _cache_loc(loc):
        try:
            st.session_state.cached_location = {"location": loc, "ts": time.time()}
        except Exception:
            pass

    # 1. 尝试GPS
    location = get_location_by_gps()
    if location:
        _cache_loc(location)
        return location

    # 2. 尝试IP定位
    location = get_location_by_ip()
    if location:
        _cache_loc(location)
        return location

    # 3. 默认（中国北京）
    location = Location({
        "city": "北京",
        "region": "北京",
        "country_name": "中国",
        "latitude": 39.9,
        "longitude": 116.4,
        "timezone": "Asia/Shanghai",
        "utc_offset": "+0800",
    }, source="default")

    _cache_loc(location)
    return location


def get_location_context() -> str:
    """获取可注入AI的定位上下文"""
    loc = get_location()
    return loc.to_ai_context()


def get_location_display() -> str:
    """获取用于UI显示的定位字符串"""
    loc = get_location()
    source_emoji = {"gps": "📍", "ip": "🌐", "default": "🏠"}
    return f"{source_emoji.get(loc.source, '📍')} {loc.display_name}"
