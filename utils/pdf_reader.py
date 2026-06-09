import fitz  # PyMuPDF
import io


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract clean text from an uploaded PDF file.
    Returns empty string if extraction fails.
    """
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        full_text = []
        for page in doc:
            text = page.get_text("text")
            full_text.append(text)

        doc.close()
        combined = "\n".join(full_text).strip()

        # Basic cleanup
        lines = [line.strip() for line in combined.splitlines() if line.strip()]
        return "\n".join(lines)

    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""
