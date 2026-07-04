from pathlib import Path

import pytest

from chef_knowledge.embeddings import ChefEmbeddings
from chef_knowledge.loader import ChefKnowledgeLoader


def test_loader_reads_text_and_html(tmp_path: Path):
    txt = tmp_path / "notes.txt"
    html = tmp_path / "site.html"
    txt.write_text("hello kitchen", encoding="utf-8")
    html.write_text("<html><body>menu plan</body></html>", encoding="utf-8")

    loader = ChefKnowledgeLoader(str(tmp_path))
    docs = loader.load_all()

    ids = {Path(d["id"]).name for d in docs}
    assert "notes.txt" in ids
    assert "site.html" in ids
    texts = "\n".join(d["text"] for d in docs)
    assert "hello kitchen" in texts
    assert "menu plan" in texts


@pytest.mark.asyncio
async def test_embeddings_shape():
    emb = ChefEmbeddings(api_key="")
    vectors = await emb.embed(["alpha", "beta"])
    assert len(vectors) == 2
    assert all(len(v) == 32 for v in vectors)
