from PyPDF2 import PdfReader

def get_pdf_text(pdf_files):
    text = ""
    for pdf in pdf_files:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

text = get_pdf_text(['/Users/markshevchenkopu/Desktop/my_projects/Hackathons/Komorebi/docs/main_guidelines.pdf'])
print(text)
