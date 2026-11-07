import io
from pypdf import PdfReader
from docx import Document as DocxDocument

class DocumentParserService:
    @staticmethod
    def parse_txt(content: bytes) -> str:
        return content.decode("utf-8", errors="ignore")

    @staticmethod
    def parse_pdf(content: bytes) -> str:
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)
        text_chunks = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_chunks.append(text)
        return "\n".join(text_chunks)

    @staticmethod
    def parse_docx(content: bytes) -> str:
        docx_file = io.BytesIO(content)
        doc = DocxDocument(docx_file)
        return "\n".join([p.text for p in doc.paragraphs if p.text])

    @classmethod
    def parse_file(cls, filename: str, content: bytes) -> str:
        filename_lower = filename.lower()
        if filename_lower.endswith(".pdf"):
            return cls.parse_pdf(content)
        elif filename_lower.endswith(".docx"):
            return cls.parse_docx(content)
        elif filename_lower.endswith((".txt", ".md")):
            return cls.parse_txt(content)
        else:
            raise ValueError(f"Unsupported file format for file: {filename}")
