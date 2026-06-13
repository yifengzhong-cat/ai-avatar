"""
AI数字分身 - 主界面 v5.0
✅ 账号系统 · MiniMax引擎 · AI评分 · 流式输出 · RAG · 多格式导出 · 键盘快捷键
"""
import streamlit as st
import sys, os, time, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils.config import config
from app.utils.styles import inject_css
from app.utils.time_utils import get_date_cn, get_time_ctx, get_time_display, get_week_range
from app.utils.error_handler import safe_ai_call, classify_error, get_user_message
from app.utils.location_utils import get_location, get_location_display, request_gps_permission, read_gps_from_storage
from app.utils.auth import register_user, login_user, update_user_profile, get_user
from app.tools.script_writer import get_llm, generate_hooks
from app.tools.script_scorer import score_script, refine_script_section
from app.tools.trend_analyzer import analyze_trend, suggest_topics, daily_hotspots
from app.tools.content_rewriter import rewrite_for_platform, generate_title_variations, reply_to_comment
from app.tools.data_analyzer import analyze_video_performance, quick_diagnose, content_calendar_suggestion
from app.tools.knowledge_base import KnowledgeBase, seed_knowledge_base, get_kb
from app.tools.content_library import ContentLibrary, get_library

st.set_page_config(page_title="AI数字分身", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
inject_css()
request_gps_permission()
read_gps_from_storage()

# ============================================
# 用量追踪
# ============================================
if "usage_tokens" not in st.session_state: st.session_state.usage_tokens = {"total": 0, "calls": 0, "cost": 0.0}
def track(text: str):
    t = int(len(text) * 1.5); st.session_state.usage_tokens["total"] += t; st.session_state.usage_tokens["calls"] += 1
    st.session_state.usage_tokens["cost"] = st.session_state.usage_tokens["total"] / 1_000_000 * 0.53  # MiniMax M3 约¥0.53/百万token

def get_full_context() -> str:
    loc = get_location()
    return f"{get_time_ctx()}\n\n{loc.to_ai_context()}"

# ============================================
# 🔐 登录/注册页面
# ============================================
if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.markdown(f"""
    <div style="text-align:center;padding:3rem 0 2rem 0;">
        <h1 style="font-size:3.2rem;background:linear-gradient(135deg,#7C3AED,#EC4899,#22D3EE);-webkit-background-clip:text;-webkit-text-fill-color:transparent;text-shadow:0 0 60px rgba(124,58,237,0.3);">🤖 AI数字分身</h1>
        <p style="font-size:1.2rem;color:#94A3B8;">短视频运营智能助手 · v5.0 · MiniMax引擎</p>
    </div>""", unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔑 登录", "📝 注册"])

    with tab_login:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 🔑 账号登录")
            login_user_id = st.text_input("用户名", placeholder="输入用户名", key="login_user")
            login_pwd = st.text_input("密码", type="password", placeholder="输入密码", key="login_pwd")
            if st.button("🔓 登录", type="primary", use_container_width=True):
                if login_user_id and login_pwd:
                    user = login_user(login_user_id, login_pwd)
                    if user:
                        st.session_state.user = user
                        st.session_state.user_profiles = {user["username"]: {"style": user["style"], "niche": user["niche"], "created": user["created_at"]}}
                        st.session_state.active_profile = user["username"]
                        st.success(f"✅ 欢迎回来，{user['nickname']}！")
                        time.sleep(0.5); st.rerun()
                    else:
                        st.error("❌ 用户名或密码错误")
                else:
                    st.warning("请输入用户名和密码")

    with tab_register:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 📝 创建账号")
            reg_user = st.text_input("用户名", placeholder="2-20个字符", key="reg_user")
            reg_nick = st.text_input("昵称（可选）", placeholder="你的名字", key="reg_nick")
            reg_pwd = st.text_input("密码", type="password", placeholder="至少4位", key="reg_pwd")
            reg_pwd2 = st.text_input("确认密码", type="password", placeholder="再输一次", key="reg_pwd2")
            reg_style = st.text_input("创作风格（可选）", placeholder="比如：幽默接地气，擅长用生活化比喻", key="reg_style")
            reg_niche = st.text_input("垂直领域（可选）", value="短视频运营", key="reg_niche")
            if st.button("✨ 注册", type="primary", use_container_width=True):
                if not reg_user or not reg_pwd:
                    st.warning("用户名和密码必填～")
                elif reg_pwd != reg_pwd2:
                    st.error("两次密码不一致")
                elif len(reg_pwd) < 4:
                    st.warning("密码至少4位")
                else:
                    ok, msg = register_user(reg_user, reg_pwd, reg_nick or reg_user, reg_style or "幽默接地气", reg_niche or "短视频运营")
                    if ok:
                        st.success(f"✅ {msg} 请切换到「登录」Tab登录～")
                    else:
                        st.error(msg)

    st.stop()

# ============================================
# 已登录 - 用户信息
# ============================================
USER = st.session_state.user
USER_ID = USER["id"]
USERNAME = USER["username"]
NICKNAME = USER["nickname"]

# 知识库（按用户隔离）
@st.cache_resource
def init_user_kb(uid: int) -> KnowledgeBase:
    from app.tools.knowledge_base import SEED_DOCUMENTS
    kb = KnowledgeBase(collection_name=f"kb_user_{uid}")
    # 仅首次导入种子数据
    if kb.count() == 0:
        for doc in SEED_DOCUMENTS:
            kb.add_document(doc["title"], doc["content"], category=doc["category"], source="系统内置")
    return kb

kb = init_user_kb(USER_ID)

# 内容库（按用户隔离）
@st.cache_resource
def init_user_lib(uid: int) -> ContentLibrary:
    return ContentLibrary(lib_file=f"content_library_user_{uid}.json")

library = init_user_lib(USER_ID)

# ============================================
# 侧边栏
# ============================================
with st.sidebar:
    st.title("🤖 AI数字分身")

    # 用户信息
    st.markdown(f"#### 👤 {NICKNAME}")
    st.caption(f"@{USERNAME} · {USER.get('niche', '短视频运营')}")
    st.caption(f"风格：{USER.get('style', '')[:30]}...")

    # 编辑个人资料
    with st.expander("⚙️ 编辑资料"):
        new_nick = st.text_input("昵称", value=NICKNAME, key="edit_nick")
        new_style = st.text_input("风格", value=USER.get("style", ""), key="edit_style")
        new_niche = st.text_input("领域", value=USER.get("niche", "短视频运营"), key="edit_niche")
        if st.button("💾 保存", key="save_profile"):
            update_user_profile(USER_ID, nickname=new_nick, style=new_style, niche=new_niche)
            USER["nickname"] = new_nick; USER["style"] = new_style; USER["niche"] = new_niche
            st.success("✅ 已保存！"); st.rerun()

    st.caption(f"📅 {get_date_cn()} | ⏰ {get_time_display()}")
    st.caption(get_location_display())

    if config.validate(): st.success("✅ MiniMax已连接")
    else: st.error("⚠️ 未配置Key")

    st.divider()

    page = st.radio("📋 导航", [
        "🏠 工作台", "🎬 脚本生成器", "🔥 热点分析", "✍️ 内容改写",
        "📊 数据分析", "📚 知识库", "📦 内容库", "💬 数字分身",
    ])

    st.divider()

    # 用量
    u = st.session_state.usage_tokens
    c1, c2 = st.columns(2)
    with c1: st.metric("📚 知识", f"{kb.count()}条")
    with c2: st.metric("📦 内容", f"{library.get_stats()['total']}条")
    st.caption(f"📊 Token: {u['total']:,} · {u['calls']}次 · ≈¥{u['cost']:.4f}")

    st.markdown("""<div style="display:flex;gap:4px;flex-wrap:wrap;">
        <span style="background:rgba(34,211,238,0.15);color:#22D3EE;padding:2px 8px;border-radius:10px;font-size:0.65rem;">🟢 MiniMax</span>
        <span style="background:rgba(244,114,182,0.15);color:#F472B6;padding:2px 8px;border-radius:10px;font-size:0.65rem;">📍 定位</span>
        <span style="background:rgba(124,58,237,0.2);color:#A78BFA;padding:2px 8px;border-radius:10px;font-size:0.65rem;">v5.0</span>
    </div>""", unsafe_allow_html=True)

    if st.button("🚪 退出登录", use_container_width=True):
        st.session_state.user = None; st.session_state.usage_tokens = {"total":0,"calls":0,"cost":0.0}
        st.rerun()

# ============================================
# 标题
# ============================================
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;">
    <div>
        <h1 style="margin:0;">🤖 {NICKNAME}的AI数字分身</h1>
        <p style="color:#94A3B8;margin:0;">@{USERNAME} · {USER.get('niche','')} · {get_date_cn()} · {get_location_display()}</p>
    </div>
    <span class="badge-glow" style="font-size:0.8rem;padding:0.3rem 1rem;">⚡ v5.0 MiniMax</span>
</div>""", unsafe_allow_html=True)

if not config.validate(): st.warning("⚠️ API Key未配置！"); st.stop()

# ============================================
# 🏠 工作台
# ============================================
if page == "🏠 工作台":
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.metric("📝 脚本", "随时可用", "6类型")
    with c2: st.metric("🔥 热点", "每日", "多平台")
    with c3: st.metric("📚 知识", f"{kb.count()}条", f"{len(kb.get_categories())}类")
    with c4: st.metric("📦 内容", f"{library.get_stats()['total']}条")
    with c5: st.metric("💰 花费", f"¥{u['cost']:.4f}", f"{u['calls']}次")
    st.divider()
    q1, q2 = st.columns(2)
    with q1:
        st.markdown("#### 🚀 快速生成")
        qt = st.text_input("主题", placeholder="打工人要不要裸辞", key="q_topic")
        if st.button("⚡ 生成5个Hook", type="primary", use_container_width=True):
            if qt:
                with st.spinner("脑暴中..."):
                    h = safe_ai_call(generate_hooks, qt, time_context=get_full_context())
                    if h: st.success("搞定！"); st.markdown(h); library.add(f"Hook：{qt}", h, "script"); track(h)
            else: st.warning("输入主题～")
        if st.button("💡 推荐10选题", use_container_width=True):
            with st.spinner("策划中..."):
                t = safe_ai_call(suggest_topics, USER.get("niche","短视频运营"), 10, time_context=get_full_context())
                if t: st.success("选题："); st.markdown(t); track(t)
    with q2:
        st.markdown("#### 📦 最近")
        for it in library.list_all(limit=4):
            e = {"script":"🎬","analysis":"📊","rewrite":"✍️","chat":"💬"}.get(it.content_type,"📄")
            st.markdown(f"- {e} {'⭐' if it.favorite else ''} {it.title[:30]}...")
        if library.get_stats()["total"] == 0: st.info("还没有内容～")
    st.info(["💡 黄金3秒：前3秒完播率决定生死","📊 发布时间：12-13点、18-19点、21-22点","🔥 蹭热点：热点出2小时内发文流量最大","📚 把爆款脚本存知识库，AI学习你的风格","✍️ 用改写功能一条内容适配多平台","Ctrl+Enter 快速生成脚本"][int(datetime.now().strftime('%d'))%6])

# ============================================
# 🎬 脚本生成器
# ============================================
elif page == "🎬 脚本生成器":
    st.subheader("🎬 脚本生成器")
    st.caption("AI流式生成 → AI评分 → 对话精修")
    c1, c2 = st.columns(2)
    with c1:
        topic = st.text_input("📝 主题", placeholder="ChatGPT使用技巧...")
        vt = st.selectbox("🎭 类型", ["口播","剧情","Vlog","测评","干货教程","产品种草"])
        aud = st.text_input("👥 受众", placeholder="职场新人、宝妈...")
    with c2:
        dur = st.slider("⏱ 时长(秒)", 15, 180, 60, 15)
        plat = st.selectbox("📱 平台", ["抖音","小红书","视频号","B站"])
        km = st.text_input("💎 金句(可选)", placeholder="不填AI提炼")
        tc = st.text_input("🔥 热点(可选)", placeholder="最近XX很火...")

    use_kb = st.checkbox("📚 检索知识库", value=True)
    if st.button("🚀 生成脚本", type="primary", use_container_width=True):
        if not topic: st.warning("输入主题～")
        else:
            rag = ""
            if use_kb and kb.count() > 0: rag = kb.search_and_format(topic, top_k=3)
            ctx = (rag + "\n\n" + (tc or "无")) if rag else (tc or "无")
            st.markdown("#### 📝 创作中...")
            pg, res = st.empty(), st.empty()
            try:
                from langchain_core.messages import HumanMessage, SystemMessage
                from app.utils.prompts import SCRIPT_WRITER_PROMPT, PERSONA_SYSTEM_PROMPT
                llm = get_llm(temperature=0.8)
                per = PERSONA_SYSTEM_PROMPT.format(my_name=NICKNAME, my_niche=USER.get("niche",""), my_style=USER.get("style",""))
                per += f"\n\n{get_full_context()}"
                up = SCRIPT_WRITER_PROMPT.format(platform=plat, topic=topic, video_type=vt, target_audience=aud or "普通用户", duration=dur, key_message=km or "请自行提炼", trend_context=ctx)
                full = ""
                for chunk in llm.stream([SystemMessage(content=per), HumanMessage(content=up)]):
                    full += chunk.content; res.markdown(full + "▌"); pg.caption(f"{len(full)}字...")
                res.markdown(full); pg.success(f"✅ {len(full)}字"); track(full)
                library.add(f"脚本：{topic}", full, "script", {"platform":plat,"type":vt,"duration":dur})
                st.session_state.script = full
                st.session_state.sinfo = {"platform":plat,"type":vt,"duration":dur,"audience":aud or "普通用户","topic":topic}
                c_d1, c_d2 = st.columns(2)
                with c_d1: st.download_button("📥 下载", full, file_name=f"脚本_{topic}.md")
                with c_d2:
                    if st.button("💾 存知识库", use_container_width=True):
                        kb.add_document(f"脚本：{topic}", full, category="我的脚本", source="AI生成"); st.success("✅ 已存！"); st.rerun()
            except Exception as e:
                st.error(get_user_message(classify_error(e), str(e)))

    if "script" in st.session_state:
        st.divider(); st.markdown("### 🔍 评分 & 精修")
        c_s, c_r = st.columns(2)
        with c_s:
            if st.button("📊 AI评分", type="primary", use_container_width=True):
                with st.spinner("评分中..."):
                    si = st.session_state.sinfo
                    sc = safe_ai_call(score_script, st.session_state.script, si["platform"], si["type"], si["duration"], si["audience"])
                    if sc: st.success("评分："); st.markdown(sc); track(sc)
        with c_r:
            rs = st.text_input("改哪里？", placeholder="开头Hook、第二段文案...", key="ref_sec")
            ri = st.text_input("怎么改？", placeholder="更口语化、加悬念...", key="ref_inst")
            if st.button("✏️ 精修", use_container_width=True):
                if rs and ri:
                    with st.spinner("精修中..."):
                        rf = safe_ai_call(refine_script_section, st.session_state.script, rs, ri)
                        if rf: st.success("精修完成！"); st.markdown(rf); st.session_state.script = rf; track(rf); library.add(f"精修：{si['topic']}", rf, "script")
                else: st.warning("填改哪里+怎么改～")

# ============================================
# 🔥 热点分析
# ============================================
elif page == "🔥 热点分析":
    st.subheader("🔥 热点分析")
    t1, t2, t3 = st.tabs(["🔍 分析", "📋 选题", "🌐 趋势"])
    with t1:
        tt = st.text_area("热点话题", placeholder="描述你想分析的热点...")
        td = st.text_area("数据(可选)", placeholder="播放量、参与人数...")
        if st.button("🔍 分析", type="primary") and tt:
            with st.spinner("分析中..."):
                r = safe_ai_call(analyze_trend, tt, td, time_context=get_full_context())
                if r: st.success("完成！"); st.markdown(r); library.add(f"热点：{tt[:30]}", r, "analysis"); track(r)
    with t2:
        ni = st.text_input("领域", value=USER.get("niche",""), key="t2_n")
        tc2 = st.slider("数量", 5, 20, 10, key="t2_c")
        if st.button("💡 推荐", type="primary"):
            with st.spinner("策划中..."):
                r = safe_ai_call(suggest_topics, ni, tc2, time_context=get_full_context())
                if r: st.success("选题："); st.markdown(r); track(r)
    with t3:
        if st.button("🌐 查看趋势", type="primary"):
            with st.spinner("汇总中..."):
                r = safe_ai_call(daily_hotspots, time_context=get_full_context())
                if r: st.success("趋势："); st.markdown(r); track(r)

# ============================================
# ✍️ 内容改写
# ============================================
elif page == "✍️ 内容改写":
    st.subheader("✍️ 多平台改写")
    c1, c2 = st.columns([2, 1])
    with c1:
        li = library.list_all(limit=10); preset = ""
        if li:
            sel = st.selectbox("从内容库选(可选)", ["不选"]+[f"{i.content_type}: {i.title[:40]}" for i in li])
            if sel != "不选":
                idx = [f"{i.content_type}: {i.title[:40]}" for i in li].index(sel); preset = li[idx].content
        orig = st.text_area("📄 粘贴内容", value=preset, placeholder="把要改写的内容粘贴到这里...", height=200)
    with c2:
        src = st.selectbox("📤 来源", ["抖音","小红书","视频号","B站","公众号","通用"])
        tgt = st.selectbox("📥 目标", ["抖音","小红书","视频号","B站"])
    if st.button("✍️ 改写", type="primary", use_container_width=True):
        if not orig: st.warning("粘贴内容～")
        else:
            with st.spinner("改写中..."):
                r = safe_ai_call(rewrite_for_platform, orig, tgt, src, time_context=get_full_context())
                if r: st.success("完成！"); st.markdown(r); library.add(f"改写：{tgt}版", r, "rewrite"); track(r)

# ============================================
# 📊 数据分析
# ============================================
elif page == "📊 数据分析":
    st.subheader("📊 数据分析")
    t1, t2, t3 = st.tabs(["📈 快速诊断", "📝 深度分析", "📅 排期"])
    with t1:
        c1, c2, c3 = st.columns(3)
        with c1: vv = st.number_input("👁 播放", 0, value=10000, step=1000); ll = st.number_input("❤️ 点赞", 0, value=500, step=100)
        with c2: cc = st.number_input("💬 评论", 0, value=50, step=10); ss = st.number_input("🔄 分享", 0, value=100, step=10)
        with c3: fg = st.number_input("👥 涨粉", 0, value=30, step=5); pd = st.number_input("⏱ 播放时长(s)", 0.0, value=15.0); vd = st.number_input("🎬 总时长(s)", 1.0, value=60.0)
        if st.button("📈 诊断", type="primary", use_container_width=True):
            with st.spinner("分析中..."):
                r = safe_ai_call(quick_diagnose, views=vv, likes=ll, comments=cc, shares=ss, followers_gain=fg, play_duration=pd, video_duration=vd, time_context=get_full_context())
                if r: st.success("完成！"); st.markdown(r); library.add(f"诊断：{vv}播放", r, "analysis"); track(r)
    with t2:
        di = st.text_area("粘贴数据", placeholder="播放/点赞/评论/分享/完播率...", height=250)
        if st.button("📝 深度分析", type="primary") and di:
            with st.spinner("分析中..."):
                r = safe_ai_call(analyze_video_performance, di, time_context=get_full_context())
                if r: st.success("完成！"); st.markdown(r); track(r)
    with t3:
        sn = st.text_input("账号类型", value=USER.get("niche",""), key="sn")
        if st.button("📅 生成排期", type="primary"):
            with st.spinner("规划中..."):
                r = safe_ai_call(content_calendar_suggestion, sn, time_context=get_full_context())
                if r: st.success("排期："); st.markdown(r); track(r)

# ============================================
# 📚 知识库
# ============================================
elif page == "📚 知识库":
    st.subheader("📚 知识库")
    sts = kb.get_stats()
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📄 文档", sts["total_docs"])
    with c2: st.metric("🧩 知识块", sts["total_chunks"])
    with c3: st.metric("📂 分类", len(sts["categories"]))

    k1, k2, k3 = st.tabs(["➕ 添加", "📋 查看", "🔍 检索"])
    with k1:
        kt = st.text_input("📌 标题", placeholder="爆款口播模板")
        kc = st.text_area("📝 内容", placeholder="粘贴脚本/文案...", height=200)
        kcat = st.selectbox("🏷 分类", ["我的脚本","脚本模板","行业知识","个人素材","竞品参考","通用"])
        if st.button("💾 添加", type="primary"):
            if kt and kc: n = kb.add_document(kt, kc, category=kcat); st.success(f"✅ 已添加！{n}个块"); st.rerun()
            else: st.warning("填标题+内容～")
        uf = st.file_uploader("📁 上传文件（PDF/TXT/MD/JSON）", type=["txt","md","json","pdf"])
        if uf:
            fb = uf.read(); ext = os.path.splitext(uf.name)[1].lower()
            if ext == ".pdf":
                from app.tools.knowledge_base import extract_text_from_file
                try: content = extract_text_from_file(uf.name, fb); st.success(f"✅ PDF：{len(content)}字符")
                except Exception as e: st.error(f"❌ {e}"); content = ""
            else: content = fb.decode("utf-8", errors="replace")
            if content and st.button("💾 上传", type="primary", key="upbtn"):
                n = kb.add_document(uf.name, content, category=kcat); st.success(f"✅ 已上传！{n}个块"); st.rerun()
    with k2:
        if sts["total_docs"] == 0: st.info("📭 空的")
        else:
            fc = st.selectbox("筛选", ["全部"]+sts["categories"])
            ds = sts["docs"] if fc == "全部" else [d for d in sts["docs"] if d["category"] == fc]
            for d in ds:
                with st.expander(f"📄 {d['title']} [{d['category']}]"):
                    if st.button("🗑 删除", key=f"kd_{d['title']}"): kb.delete_document(d['title']); st.success("已删除"); st.rerun()
    with k3:
        tq = st.text_input("搜索", placeholder="抖音算法、hook...")
        if st.button("🔍 检索", type="primary") and tq:
            rs = kb.search(tq, top_k=3)
            if rs:
                for i, r in enumerate(rs, 1):
                    with st.expander(f"结果{i}：{r['metadata']['title']} ({r['score']:.0%})"): st.markdown(r["content"])
            else: st.warning("没有找到")

# ============================================
# 📦 内容库
# ============================================
elif page == "📦 内容库":
    st.subheader("📦 内容库"); ls = library.get_stats()
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📦 总计", ls["total"])
    with c2: st.metric("⭐ 收藏", ls["favorites"])
    with c3: st.metric("📝 脚本", ls["by_type"].get("script",0))
    with c4: st.metric("📊 分析", ls["by_type"].get("analysis",0))
    fc1, fc2, fc3 = st.columns(3)
    with fc1: tf = st.selectbox("类型", ["全部","script","analysis","rewrite","chat"])
    with fc2: sf = st.text_input("🔍 搜索", placeholder="标题或内容...")
    with fc3: ff = st.checkbox("⭐ 仅收藏")
    items = library.list_all(content_type=None if tf=="全部" else tf, search=sf, favorites_only=ff)
    if not items: st.info("📭 还没有内容")
    else:
        for it in items:
            e = {"script":"🎬","analysis":"📊","rewrite":"✍️","chat":"💬"}.get(it.content_type,"📄")
            with st.expander(f"{e} {it.title[:60]} {'⭐' if it.favorite else ''} [{it.content_type}]"):
                st.markdown(it.content[:2000])
                if len(it.content) > 2000: st.caption(f"...{len(it.content)}字")
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    if st.button("⭐" if not it.favorite else "★", key=f"fv_{it.id}"): library.toggle_favorite(it.id); st.rerun()
                with c2: st.download_button("📥", it.content, file_name=f"{it.title[:30]}.md", mime="text/markdown", key=f"dl_{it.id}")
                with c3:
                    if st.button("📋 复制", key=f"cp_{it.id}"): st.code(it.content[:500]+("..." if len(it.content)>500 else ""));
                with c4:
                    if st.button("🗑", key=f"d_{it.id}"): library.delete(it.id); st.success("已删除"); st.rerun()
    if ls["total"] > 0:
        st.divider(); st.download_button("📥 导出全部(Markdown)", library.export_all(), file_name="AI数字分身_导出.md")

# ============================================
# 💬 数字分身
# ============================================
elif page == "💬 数字分身":
    st.subheader("💬 数字分身"); st.caption(f"👤 {NICKNAME} · 📚{kb.count()}条 · ⚡流式")
    if "msgs" not in st.session_state: st.session_state.msgs = []
    for m in st.session_state.msgs:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    if not st.session_state.msgs:
        st.chat_message("assistant").markdown(f"嘿 {NICKNAME}！👋\n\n我是你的数字分身，风格：{USER.get('style','')[:40]}...\n\n📍 {get_location_display()} · {get_date_cn()}\n\n试试：写脚本 / 分析热点 / 看数据 / 改写文案 😎")
    if p := st.chat_input("💬 输入..."):
        st.session_state.msgs.append({"role":"user","content":p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            rag_ctx = kb.search_and_format(p, top_k=3) if kb.count() > 0 else ""
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage, SystemMessage
                from app.utils.prompts import PERSONA_SYSTEM_PROMPT
                llm = ChatOpenAI(model=config.LLM_MODEL, api_key=config.OPENAI_API_KEY, base_url=config.OPENAI_BASE_URL, temperature=0.8, streaming=True)
                per = PERSONA_SYSTEM_PROMPT.format(my_name=NICKNAME, my_niche=USER.get("niche",""), my_style=USER.get("style",""))
                per += f"\n\n{get_full_context()}"
                if rag_ctx: per += f"\n\n{rag_ctx}\n\n优先参考知识库。"
                h = [SystemMessage(content=per)]
                for m in st.session_state.msgs[-8:]:
                    if m["role"]=="user": h.append(HumanMessage(content=m["content"]))
                rp = st.empty(); full = ""
                for chunk in llm.stream(h): full += chunk.content; rp.markdown(full + "▌")
                rp.markdown(full); track(full)
                library.add(f"对话：{p[:40]}", full, "chat"); st.session_state.msgs.append({"role":"assistant","content":full})
                if rag_ctx:
                    with st.expander("🔍 参考知识库"): st.markdown(rag_ctx[:500])
            except Exception as e:
                st.error(get_user_message(classify_error(e), str(e)))
