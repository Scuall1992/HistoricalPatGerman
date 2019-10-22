import re
import io
import os
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
import argparse


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


def replace_smht(s, what):
    for i in what:
        s = s.replace(i, '', 1)
    return s


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("filename", type=str)

    file = args.parse_args().filename
    # file = r"C:\pat\pat_Patentblatt_192545.pdf"

    try:
        if ".pdf" in file:
            data = extract_text_from_pdf(f'{file}')

            res = [(m.start(0), m.end(0)) for m in
                   re.finditer(r" [0-9]{1,2}(\.|,)( )*[0-9]{1,2}(\.|,)( )*[0-9]{1,2}", data)]
            parsed = []

            for i in range(len(res) - 1):
                parsed.append(data[res[i][1]:res[i + 1][1]].replace(". ", "", 1))

            # with open("replace_cases") as rep:
            #     for c in rep.read().split("\n"):
            #         parsed = [i.replace(*c.split(',')) for i in parsed]

            with open(f"{file}.csv", "w", encoding="utf-8") as f:
                f.write("\n".join(parsed))
    except Exception as e:
        print(file, e)

# #Erteilungen
# #Zurücknahme von Anmeldungen
