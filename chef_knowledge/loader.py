from pathlib import Path
import re
from typing import Dict, List


class ChefKnowledgeLoader:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    def load_all(self) -> List[Dict[str, str]]:
        docs: List[Dict[str, str]] = []
        if not self.base_path.exists():
            return docs

        for file in self.base_path.rglob("*"):
            if not file.is_file():
                continue
            text = self._extract_text(file)
            if text:
                docs.append({"id": str(file), "text": text})
        return docs

    def _extract_text(self, file: Path) -> str:
        try:
            suffix = file.suffix.lower()
            if suffix in {".txt", ".md", ".py", ".json"}:
                return file.read_text(encoding="utf-8", errors="ignore")
            if suffix in {".html", ".htm"}:
                raw = file.read_text(encoding="utf-8", errors="ignore")
                return re.sub(r"<[^>]+>", "", raw)
            return ""
        except Exception:
            return ""
