"""
AI数字分身 - 用户认证系统
SQLite存储，密码SHA256加盐哈希
每用户独立数据空间
"""
import os
import json
import hashlib
import secrets
import sqlite3
from datetime import datetime
from typing import Optional

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
DB_FILE = os.path.join(DATA_DIR, "users.db")
os.makedirs(DATA_DIR, exist_ok=True)


# ============================================
# 数据库初始化
# ============================================
def get_db() -> sqlite3.Connection:
    """获取数据库连接"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化用户表"""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            nickname TEXT DEFAULT '',
            style TEXT DEFAULT '幽默接地气',
            niche TEXT DEFAULT '短视频运营',
            created_at TEXT DEFAULT (datetime('now','localtime')),
            last_login TEXT
        )
    """)
    conn.commit()
    conn.close()


# ============================================
# 密码哈希
# ============================================
def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """SHA256加盐哈希，返回 (hash, salt)"""
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.sha256((password + salt).encode()).hexdigest()
    return h, salt


# ============================================
# 用户操作
# ============================================
def register_user(username: str, password: str, nickname: str = "", style: str = "幽默接地气", niche: str = "短视频运营") -> tuple[bool, str]:
    """
    注册新用户

    返回: (成功?, 消息)
    """
    username = username.strip().lower()
    if len(username) < 2:
        return False, "用户名至少2个字符"
    if len(password) < 4:
        return False, "密码至少4个字符"

    conn = get_db()
    try:
        # 检查是否已存在
        existing = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            return False, "用户名已被注册"

        pw_hash, salt = hash_password(password)
        conn.execute(
            "INSERT INTO users (username, password_hash, salt, nickname, style, niche) VALUES (?, ?, ?, ?, ?, ?)",
            (username, pw_hash, salt, nickname or username, style, niche),
        )
        conn.commit()
        return True, "注册成功！"
    except Exception as e:
        return False, f"注册失败：{str(e)}"
    finally:
        conn.close()


def login_user(username: str, password: str) -> Optional[dict]:
    """
    登录验证

    返回: 用户信息dict或None
    """
    username = username.strip().lower()
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,),
        ).fetchone()

        if not user:
            return None

        pw_hash, _ = hash_password(password, user["salt"])
        if pw_hash != user["password_hash"]:
            return None

        # 更新最后登录时间
        conn.execute(
            "UPDATE users SET last_login = datetime('now','localtime') WHERE id = ?",
            (user["id"],),
        )
        conn.commit()

        return {
            "id": user["id"],
            "username": user["username"],
            "nickname": user["nickname"] or user["username"],
            "style": user["style"],
            "niche": user["niche"],
            "created_at": user["created_at"],
        }
    finally:
        conn.close()


def update_user_profile(user_id: int, **kwargs) -> bool:
    """更新用户信息"""
    allowed = ["nickname", "style", "niche"]
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return False

    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [user_id]

    conn = get_db()
    try:
        conn.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return True
    finally:
        conn.close()


def get_user(user_id: int) -> Optional[dict]:
    """获取用户信息"""
    conn = get_db()
    try:
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if user:
            return {
                "id": user["id"],
                "username": user["username"],
                "nickname": user["nickname"] or user["username"],
                "style": user["style"],
                "niche": user["niche"],
                "created_at": user["created_at"],
            }
        return None
    finally:
        conn.close()


# ============================================
# 初始化
# ============================================
init_db()
