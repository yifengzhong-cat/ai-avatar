"""
AI数字分身 - 内容库
本地JSON存储，管理所有AI生成的内容

功能：
- 自动保存生成的内容（防丢失）
- 搜索、筛选、收藏
- 导出为文件
- 一键复用（作为改写/分析的输入）
"""
import json
import os
import uuid
from datetime import datetime
from typing import Optional

# 数据目录
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")
LIBRARY_FILE = os.path.join(DATA_DIR, "content_library.json")
os.makedirs(DATA_DIR, exist_ok=True)


# ============================================
# 数据模型
# ============================================
class ContentItem:
    """内容条目"""
    def __init__(
        self,
        title: str,
        content: str,
        content_type: str,  # script / analysis / rewrite / chat
        metadata: dict = None,
        item_id: str = None,
    ):
        self.id = item_id or str(uuid.uuid4())[:8]
        self.title = title
        self.content = content
        self.content_type = content_type
        self.metadata = metadata or {}
        self.metadata.setdefault("created_at", datetime.now().isoformat())
        self.metadata.setdefault("tags", [])
        self.favorite = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "content_type": self.content_type,
            "metadata": self.metadata,
            "favorite": self.favorite,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContentItem":
        item = cls(
            title=data["title"],
            content=data["content"],
            content_type=data["content_type"],
            metadata=data.get("metadata", {}),
            item_id=data["id"],
        )
        item.favorite = data.get("favorite", False)
        return item


# ============================================
# 内容库管理
# ============================================
class ContentLibrary:
    """内容库管理器"""

    def __init__(self, lib_file: str = None):
        self.lib_file = lib_file or "content_library.json"
        self.items: list[ContentItem] = []
        self._load()

    @property
    def _filepath(self) -> str:
        return os.path.join(DATA_DIR, self.lib_file)

    def _load(self):
        """从文件加载"""
        if os.path.exists(self._filepath):
            try:
                with open(self._filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.items = [ContentItem.from_dict(d) for d in data]
            except (json.JSONDecodeError, KeyError):
                self.items = []

    def _save(self):
        """保存到文件"""
        with open(self._filepath, "w", encoding="utf-8") as f:
            json.dump(
                [item.to_dict() for item in self.items],
                f,
                ensure_ascii=False,
                indent=2,
            )

    # ==========================================
    # CRUD操作
    # ==========================================
    def add(
        self,
        title: str,
        content: str,
        content_type: str = "script",
        metadata: dict = None,
    ) -> ContentItem:
        """添加内容"""
        item = ContentItem(
            title=title,
            content=content,
            content_type=content_type,
            metadata=metadata,
        )
        self.items.insert(0, item)  # 最新的排前面
        self._save()
        return item

    def delete(self, item_id: str) -> bool:
        """删除内容"""
        before = len(self.items)
        self.items = [i for i in self.items if i.id != item_id]
        if len(self.items) < before:
            self._save()
            return True
        return False

    def toggle_favorite(self, item_id: str) -> bool:
        """切换收藏状态"""
        for item in self.items:
            if item.id == item_id:
                item.favorite = not item.favorite
                self._save()
                return item.favorite
        return False

    def get(self, item_id: str) -> Optional[ContentItem]:
        """获取单条内容"""
        for item in self.items:
            if item.id == item_id:
                return item
        return None

    # ==========================================
    # 查询
    # ==========================================
    def list_all(
        self,
        content_type: str = None,
        search: str = "",
        favorites_only: bool = False,
        limit: int = 50,
    ) -> list[ContentItem]:
        """列表查询"""
        results = self.items

        if content_type:
            results = [i for i in results if i.content_type == content_type]
        if search:
            search_lower = search.lower()
            results = [
                i for i in results
                if search_lower in i.title.lower()
                or search_lower in i.content.lower()
            ]
        if favorites_only:
            results = [i for i in results if i.favorite]

        return results[:limit]

    def get_stats(self) -> dict:
        """统计信息"""
        types = {}
        for item in self.items:
            t = item.content_type
            types[t] = types.get(t, 0) + 1

        return {
            "total": len(self.items),
            "favorites": sum(1 for i in self.items if i.favorite),
            "by_type": types,
            "latest": self.items[0] if self.items else None,
        }

    def export_all(self) -> str:
        """导出全部内容为Markdown"""
        lines = ["# 📦 AI数字分身 - 内容库导出", f"导出时间：{datetime.now().isoformat()}", "", "---", ""]
        for item in self.items:
            lines.append(f"## {item.title}")
            lines.append(f"类型：{item.content_type} | ID：{item.id} | {'⭐' if item.favorite else ''}")
            lines.append("")
            lines.append(item.content)
            lines.append("")
            lines.append("---")
            lines.append("")
        return "\n".join(lines)


# ============================================
# 全局单例（Streamlit session级别）
# ============================================
_library_instance: Optional[ContentLibrary] = None


def get_library() -> ContentLibrary:
    """获取内容库实例"""
    global _library_instance
    if _library_instance is None:
        _library_instance = ContentLibrary()
    return _library_instance


def reset_library():
    """重置内容库（用于测试）"""
    global _library_instance
    _library_instance = None
