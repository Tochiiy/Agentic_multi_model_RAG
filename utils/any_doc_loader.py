
from langchain_community.document_loaders import (
    PyPDFLoader,           # PDF
    Docx2txtLoader,        # Word .docx
    TextLoader,            # .txt
    CSVLoader,             # .csv
    UnstructuredExcelLoader, # .xlsx
    UnstructuredPowerPointLoader,  # .pptx
)
from langchain_core.documents import Document
from typing import List
import os
import dotenv

dotenv.load_dotenv()


# ── PDF ───────────────────────────────────────────────────────────
def load_pdf(path: str) -> List[Document]:
    loader = PyPDFLoader(path)
    docs = loader.load()
    for i, doc in enumerate(docs):
        doc.metadata["doc_type"] = "pdf"
        doc.metadata["page"] = i + 1
        doc.metadata["source"] = path
    print(f"  ✅ PDF: {len(docs)} pages from {os.path.basename(path)}")
    return docs


# ── Word .docx ────────────────────────────────────────────────────
def load_docx(path: str) -> List[Document]:
    loader = Docx2txtLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["doc_type"] = "docx"
        doc.metadata["source"] = path
    print(f"  ✅ DOCX: {len(docs)} doc(s) from {os.path.basename(path)}")
    return docs


# ── Plain Text ────────────────────────────────────────────────────
def load_txt(path: str) -> List[Document]:
    loader = TextLoader(path, encoding="utf-8")
    docs = loader.load()
    for doc in docs:
        doc.metadata["doc_type"] = "txt"
        doc.metadata["source"] = path
    print(f"  ✅ TXT: {len(docs)} doc(s) from {os.path.basename(path)}")
    return docs


# ── CSV ───────────────────────────────────────────────────────────
def load_csv(path: str) -> List[Document]:
    loader = CSVLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["doc_type"] = "csv"
        doc.metadata["source"] = path
    print(f"  ✅ CSV: {len(docs)} rows from {os.path.basename(path)}")
    return docs


# ── Excel .xlsx ───────────────────────────────────────────────────
def load_excel(path: str) -> List[Document]:
    loader = UnstructuredExcelLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["doc_type"] = "xlsx"
        doc.metadata["source"] = path
    print(f"  ✅ XLSX: {len(docs)} sheet(s) from {os.path.basename(path)}")
    return docs


# ── PowerPoint .pptx ─────────────────────────────────────────────
def load_pptx(path: str) -> List[Document]:
    loader = UnstructuredPowerPointLoader(path)
    docs = loader.load()
    for doc in docs:
        doc.metadata["doc_type"] = "pptx"
        doc.metadata["source"] = path
    print(f"  ✅ PPTX: {len(docs)} slide(s) from {os.path.basename(path)}")
    return docs


# ── Universal Loader ──────────────────────────────────────────────
def load_document(path: str) -> List[Document]:
    """
    Detects file type by extension and loads accordingly.

    Supported:
        .pdf   → PyPDFLoader
        .docx  → Docx2txtLoader
        .txt   → TextLoader
        .csv   → CSVLoader
        .xlsx  → UnstructuredExcelLoader
        .pptx  → UnstructuredPowerPointLoader
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    loaders = {
        ".pdf":  load_pdf,
        ".docx": load_docx,
        ".txt":  load_txt,
        ".csv":  load_csv,
        ".xlsx": load_excel,
        ".pptx": load_pptx,
    }

    if ext not in loaders:
        raise ValueError(f"Unsupported file type: {ext}\nSupported: {list(loaders.keys())}")

    return loaders[ext](path)


# ── Load Multiple Files ───────────────────────────────────────────
def load_documents(paths: List[str]) -> List[Document]:
    """
    Load multiple files of any supported type.

    Usage:
        docs = load_documents([
            "research.pdf",
            "notes.docx",
            "data.csv",
            "slides.pptx"
        ])
    """
    all_docs = []
    for path in paths:
        try:
            docs = load_document(path)
            all_docs.extend(docs)
        except Exception as e:
            print(f"  ❌ Failed to load {path}: {e}")
    return all_docs


# ── Test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    # test with a file path argument
    # python -m utils.pdf_loader test.pdf
    if len(sys.argv) > 1:
        path = sys.argv[1]
        docs = load_document(path)
        print(f"\nLoaded {len(docs)} document(s)")
        print(f"Preview:\n{docs[0].page_content[:500]}")
    else:
        print("Usage: python -m utils.pdf_loader <file_path>")
        print("Supported: .pdf .docx .txt .csv .xlsx .pptx")