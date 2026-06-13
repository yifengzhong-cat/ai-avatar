"""
AI数字分身 - 赛博毛玻璃UI主题 v3.5
Glassmorphism + Neon Glow + Animated Gradients
"""
import streamlit as st


COLORS = {
    "primary": "#7C3AED",
    "primary_light": "#A78BFA",
    "primary_dark": "#5B21B6",
    "accent": "#F472B6",
    "accent_light": "#F9A8D4",
    "neon_cyan": "#22D3EE",
    "neon_green": "#34D399",
    "danger": "#FB7185",
    "warning": "#FBBF24",
    "bg_dark": "#0F0F23",
    "bg_glass": "rgba(255, 255, 255, 0.05)",
    "glass_border": "rgba(255, 255, 255, 0.12)",
    "glass_shadow": "rgba(124, 58, 237, 0.15)",
    "text_primary": "#F1F5F9",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "gradient_hero": "linear-gradient(135deg, #7C3AED 0%, #EC4899 50%, #F472B6 100%)",
    "gradient_card": "linear-gradient(145deg, rgba(124,58,237,0.1), rgba(236,72,153,0.05))",
    "gradient_glow": "linear-gradient(135deg, #7C3AED, #EC4899, #22D3EE)",
}


def inject_css():
    css = f"""
    <style>
    /* ============================================
       导入字体
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    /* ============================================
       全局基础 - 暗色赛博风
       ============================================ */
    .stApp {{
        background: {COLORS["bg_dark"]};
        background-image:
            radial-gradient(ellipse 80% 50% at 50% -20%, rgba(124,58,237,0.15), transparent),
            radial-gradient(ellipse 60% 40% at 90% 80%, rgba(236,72,153,0.08), transparent),
            radial-gradient(ellipse 50% 30% at 10% 50%, rgba(34,211,238,0.06), transparent);
        background-attachment: fixed;
    }}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }}

    /* ============================================
       星空粒子动画（背景微动效）
       ============================================ */
    @keyframes floatParticle {{
        0%, 100% {{ transform: translateY(0) rotate(0deg); opacity: 0.3; }}
        33% {{ transform: translateY(-20px) rotate(120deg); opacity: 0.6; }}
        66% {{ transform: translateY(-10px) rotate(240deg); opacity: 0.4; }}
    }}

    @keyframes pulseGlow {{
        0%, 100% {{ box-shadow: 0 0 20px rgba(124,58,237,0.2), 0 0 60px rgba(124,58,237,0.05); }}
        50% {{ box-shadow: 0 0 35px rgba(236,72,153,0.3), 0 0 80px rgba(124,58,237,0.1); }}
    }}

    @keyframes shimmer {{
        0% {{ background-position: -200% center; }}
        100% {{ background-position: 200% center; }}
    }}

    @keyframes borderGlow {{
        0%, 100% {{ border-color: rgba(124,58,237,0.3); box-shadow: 0 0 15px rgba(124,58,237,0.1); }}
        50% {{ border-color: rgba(236,72,153,0.4); box-shadow: 0 0 25px rgba(236,72,153,0.15); }}
    }}

    /* ============================================
       标题样式 - 霓虹渐变
       ============================================ */
    h1 {{
        font-family: 'Space Grotesk', 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
        font-weight: 800 !important;
        font-size: 2.4rem !important;
        background: {COLORS["gradient_hero"]};
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
        letter-spacing: -0.5px;
        text-shadow: 0 0 40px rgba(124,58,237,0.3);
    }}

    h2 {{
        font-family: 'Space Grotesk', 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        color: {COLORS["text_primary"]} !important;
    }}

    h3 {{
        font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        color: {COLORS["text_primary"]} !important;
    }}

    /* 英文标题特殊字体 */
    .stMarkdown p strong, .stMarkdown li strong {{
        color: {COLORS["primary_light"]};
    }}

    /* ============================================
       毛玻璃卡片
       ============================================ */
    .glass-card {{
        background: {COLORS["bg_glass"]};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {COLORS["glass_border"]};
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}

    .glass-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    }}

    .glass-card:hover {{
        border-color: rgba(124,58,237,0.4);
        box-shadow: 0 12px 40px rgba(124,58,237,0.15);
        transform: translateY(-2px);
    }}

    .glass-card-glow {{
        background: {COLORS["bg_glass"]};
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid {COLORS["glass_border"]};
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        animation: pulseGlow 3s ease-in-out infinite;
        transition: all 0.4s ease;
    }}

    /* ============================================
       渐变色英雄卡片
       ============================================ */
    .hero-card {{
        background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(236,72,153,0.15), rgba(34,211,238,0.1));
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        position: relative;
        overflow: hidden;
    }}

    .hero-card::after {{
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
        animation: floatParticle 8s ease-in-out infinite;
    }}

    /* ============================================
       Metric卡片覆盖 - 毛玻璃数据卡
       ============================================ */
    [data-testid="stMetric"] {{
        background: {COLORS["bg_glass"]} !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid {COLORS["glass_border"]} !important;
        border-radius: 16px !important;
        padding: 1rem 1.2rem !important;
        transition: all 0.3s ease;
    }}

    [data-testid="stMetric"]:hover {{
        border-color: rgba(124,58,237,0.3) !important;
        box-shadow: 0 0 25px rgba(124,58,237,0.1);
    }}

    [data-testid="stMetric"] > div > div:first-child {{
        color: {COLORS["text_secondary"]} !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px;
        text-transform: uppercase;
    }}

    [data-testid="stMetric"] > div > div:nth-child(2) {{
        color: {COLORS["text_primary"]} !important;
        font-size: 1.8rem !important;
        font-weight: 800 !important;
    }}

    /* ============================================
       霓虹按钮
       ============================================ */
    .stButton > button {{
        border-radius: 14px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 0.65rem 1.5rem !important;
        border: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        letter-spacing: 0.5px;
        position: relative;
        overflow: hidden;
    }}

    /* Primary按钮 - 霓虹紫 */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #7C3AED, #A78BFA) !important;
        color: white !important;
        box-shadow: 0 0 25px rgba(124,58,237,0.3), 0 4px 15px rgba(0,0,0,0.2);
    }}

    .stButton > button[kind="primary"]:hover {{
        box-shadow: 0 0 40px rgba(124,58,237,0.5), 0 0 80px rgba(236,72,153,0.2);
        transform: translateY(-2px);
    }}

    .stButton > button[kind="primary"]:active {{
        transform: scale(0.97);
    }}

    /* Secondary按钮 - 毛玻璃 */
    .stButton > button[kind="secondary"] {{
        background: {COLORS["bg_glass"]} !important;
        backdrop-filter: blur(10px);
        color: {COLORS["text_primary"]} !important;
        border: 1px solid {COLORS["glass_border"]} !important;
    }}

    .stButton > button[kind="secondary"]:hover {{
        border-color: rgba(124,58,237,0.4) !important;
        box-shadow: 0 0 20px rgba(124,58,237,0.15);
    }}

    /* ============================================
       输入框 - 毛玻璃
       ============================================ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {{
        border-radius: 14px !important;
        border: 1px solid {COLORS["glass_border"]} !important;
        padding: 0.8rem 1rem !important;
        font-size: 0.95rem !important;
        background: rgba(255,255,255,0.03) !important;
        color: {COLORS["text_primary"]} !important;
        transition: all 0.3s ease !important;
    }}

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: rgba(124,58,237,0.5) !important;
        box-shadow: 0 0 25px rgba(124,58,237,0.15), 0 0 0 3px rgba(124,58,237,0.06) !important;
        background: rgba(255,255,255,0.05) !important;
    }}

    .stTextInput > div > div > input::placeholder,
    .stTextArea > div > div > textarea::placeholder {{
        color: {COLORS["text_muted"]};
    }}

    /* ============================================
       SelectBox
       ============================================ */
    .stSelectbox > div > div {{
        border-radius: 14px !important;
        background: rgba(255,255,255,0.03) !important;
        border-color: {COLORS["glass_border"]} !important;
        color: {COLORS["text_primary"]} !important;
    }}

    /* ============================================
       Tabs - 霓虹下划线
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0.5rem;
        background: transparent;
        border-bottom: 1px solid rgba(255,255,255,0.08);
        padding-bottom: 0;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 10px 10px 0 0;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 0.9rem;
        color: {COLORS["text_secondary"]};
        background: transparent;
        border: none;
    }}

    .stTabs [data-baseweb="tab"][aria-selected="true"] {{
        color: {COLORS["primary_light"]} !important;
        background: rgba(124,58,237,0.08);
        border-bottom: 3px solid {COLORS["primary"]};
        box-shadow: 0 0 15px rgba(124,58,237,0.15);
    }}

    /* ============================================
       Chat消息 - 霓虹气泡
       ============================================ */
    [data-testid="stChatMessage"] {{
        border-radius: 18px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 0.8rem !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
    }}

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {{
        background: linear-gradient(135deg, rgba(124,58,237,0.2), rgba(236,72,153,0.1)) !important;
        border: 1px solid rgba(124,58,237,0.2);
        color: {COLORS["text_primary"]} !important;
    }}

    [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {{
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid {COLORS["glass_border"]} !important;
        color: {COLORS["text_primary"]} !important;
    }}

    /* ============================================
       侧边栏 - 深色毛玻璃
       ============================================ */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(15,15,35,0.98), rgba(20,15,40,0.98)) !important;
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-right: 1px solid rgba(255,255,255,0.06);
    }}

    [data-testid="stSidebar"] * {{
        color: {COLORS["text_primary"]} !important;
    }}

    [data-testid="stSidebar"] h1 {{
        color: white !important;
        -webkit-text-fill-color: white !important;
        font-size: 1.4rem !important;
        text-shadow: 0 0 30px rgba(124,58,237,0.5);
    }}

    [data-testid="stSidebar"] .stRadio > div {{
        background: rgba(255,255,255,0.03);
        border-radius: 14px;
        padding: 0.4rem;
        border: 1px solid rgba(255,255,255,0.05);
    }}

    [data-testid="stSidebar"] .stRadio label {{
        color: {COLORS["text_secondary"]} !important;
    }}

    [data-testid="stSidebar"] .stRadio label:hover {{
        color: {COLORS["text_primary"]} !important;
    }}

    /* ============================================
       Expander - 毛玻璃折叠面板
       ============================================ */
    .streamlit-expanderHeader {{
        border-radius: 14px !important;
        background: {COLORS["bg_glass"]} !important;
        border: 1px solid {COLORS["glass_border"]} !important;
        font-weight: 600 !important;
        color: {COLORS["text_primary"]} !important;
        transition: all 0.3s ease;
    }}

    .streamlit-expanderHeader:hover {{
        border-color: rgba(124,58,237,0.3) !important;
    }}

    .streamlit-expanderContent {{
        background: rgba(255,255,255,0.02) !important;
        border-radius: 0 0 14px 14px !important;
        border: 1px solid {COLORS["glass_border"]} !important;
        border-top: none !important;
        color: {COLORS["text_primary"]} !important;
    }}

    /* ============================================
       Alert - 发光提示框
       ============================================ */
    .stAlert {{
        border-radius: 16px !important;
        border: 1px solid {COLORS["glass_border"]} !important;
        background: {COLORS["bg_glass"]} !important;
        backdrop-filter: blur(16px);
        color: {COLORS["text_primary"]} !important;
    }}

    /* ============================================
       File Uploader - 拖拽区
       ============================================ */
    [data-testid="stFileUploader"] {{
        border-radius: 18px !important;
        border: 2px dashed rgba(124,58,237,0.25) !important;
        background: rgba(124,58,237,0.03) !important;
        padding: 2rem !important;
        transition: all 0.3s ease;
    }}

    [data-testid="stFileUploader"]:hover {{
        border-color: rgba(124,58,237,0.5) !important;
        background: rgba(124,58,237,0.06) !important;
        box-shadow: 0 0 30px rgba(124,58,237,0.1);
    }}

    /* ============================================
       Divider - 渐变线
       ============================================ */
    hr {{
        margin: 1.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(124,58,237,0.3), rgba(236,72,153,0.2), transparent);
    }}

    /* ============================================
       Scrollbar - 霓虹滚动条
       ============================================ */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}

    ::-webkit-scrollbar-track {{
        background: rgba(255,255,255,0.02);
    }}

    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, rgba(124,58,237,0.3), rgba(236,72,153,0.2));
        border-radius: 3px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, rgba(124,58,237,0.5), rgba(236,72,153,0.3));
    }}

    /* ============================================
       Spinner - 霓虹加载
       ============================================ */
    .stSpinner > div {{
        border-top-color: {COLORS["primary"]} !important;
        border-right-color: {COLORS["accent"]} !important;
    }}

    /* ============================================
       Badges系统
       ============================================ */
    .badge-neon {{
        display: inline-block;
        padding: 0.25rem 0.9rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(124,58,237,0.15);
        color: {COLORS["primary_light"]};
        border: 1px solid rgba(124,58,237,0.2);
    }}

    .badge-glow {{
        display: inline-block;
        padding: 0.25rem 0.9rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(34,211,238,0.1);
        color: {COLORS["neon_cyan"]};
        border: 1px solid rgba(34,211,238,0.2);
        box-shadow: 0 0 12px rgba(34,211,238,0.1);
    }}

    /* ============================================
       密码页特殊样式
       ============================================ */
    .password-container {{
        text-align: center;
        padding: 3rem;
    }}

    /* ============================================
       Checkbox美化
       ============================================ */
    .stCheckbox label {{
        color: {COLORS["text_secondary"]} !important;
    }}

    /* ============================================
       代码块样式
       ============================================ */
    code {{
        background: rgba(124,58,237,0.1) !important;
        color: {COLORS["primary_light"]} !important;
        border-radius: 6px !important;
        padding: 0.15rem 0.4rem !important;
    }}

    /* ============================================
       提示文字
       ============================================ */
    .stCaption {{
        color: {COLORS["text_muted"]} !important;
    }}

    /* ============================================
       文本颜色覆盖（确保暗色主题可读）
       ============================================ */
    p, li, span, label, .stMarkdown {{
        color: {COLORS["text_primary"]};
    }}

    .stMarkdown p {{
        color: {COLORS["text_primary"]};
    }}

    /* ============================================
       移动端响应
       ============================================ */
    @media (max-width: 768px) {{
        h1 {{
            font-size: 1.8rem !important;
        }}
        .glass-card, .hero-card {{
            padding: 1rem;
            border-radius: 16px;
        }}
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
