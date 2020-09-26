import re
import io
import os
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import argparse

re_date_of_patent = r" [0-9]{1,2}(\.|,| )( )*[0-9]{1,2}(\.| |,)( )*[0-9]{1,2}[^0-9]"


def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    if text:
        return text


# s = extract_text_from_pdf("cities.pdf")

# with open("cities_parse.txt", "r", encoding="utf-8") as f:
#     s = f.read().replace(". .", "..")
#     while ". ." in s:
#         s = s.replace(". .", "..")
#     while " . . " in s:
#         s = s.replace(" . . ", "..")

with open("cities_parse2.txt", "r", encoding="utf-8") as g:
    data = g.read()

    res = re.sub(r"(\.){2,}", " ", data)


    buf = []


    for c in enumerate(res):
        pass


    # with open("cities_parse3.txt", "w", encoding="utf-8") as f:
    #     f.write(res)

