import pdfplumber
import docx

def extract_text_from_file(uploaded_file):
    """
    Detects file type and extracts text accordingly.
    Supported: PDF, DOCX, TXT
    """
    text = ""
    try:
        # PDF Extraction
        if uploaded_file.name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    extract = page.extract_text()
                    if extract: text += extract + "\n"
                        
        # DOCX Extraction
        elif uploaded_file.name.endswith('.docx'):
            doc = docx.Document(uploaded_file)
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        # TXT Extraction
        elif uploaded_file.name.endswith('.txt'):
            text = uploaded_file.read().decode("utf-8")
            
    except Exception as e:
        return f"Error reading file: {str(e)}"
    
    return text

def truncate_text(text, max_chars=30000):
    """
    Simple truncation to ensure we don't exceed API limits.
    Gemini can handle large text, so we set a high limit.
    """
    if len(text) <= max_chars:
        return text
    
    # Keep the beginning and end of the contract
    return text[:int(max_chars*0.75)] + "\n\n... [SECTION SKIPPED] ...\n\n" + text[-int(max_chars*0.25):]