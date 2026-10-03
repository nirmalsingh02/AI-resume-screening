from pypdf import PdfReader


def extract_text_from_pdf(file_path):

    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:

        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


if __name__ == "__main__":

    pdf_path = "data/resumes/Nirmal_Singh_Resume_ATS.pdf"

    text = extract_text_from_pdf(
        pdf_path
    )

    print("\n===== PDF TEXT =====\n")

    print(text)