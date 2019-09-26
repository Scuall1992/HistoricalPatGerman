import re
# import PyPDF2
#
# pdfFileObj = open('1.pdf','rb')     #'rb' for read binary mode
# pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
#
#
# pageObj = pdfReader.getPage(9)          #'9' is the page number
# print(pageObj.extractText())

import io

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage


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


if __name__ == '__main__':
    data = extract_text_from_pdf('1.pdf')
    # res = re.split(r"[0-9]{1,2}\.( )*[0-9]{1,2}\.( )*[0-9]{1,2}", data)
    res = re.findall(r"[0-9]{1,2}\.( )*[0-9]{1,2}\.( )*[0-9]{1,2}", data)
    print("awd")