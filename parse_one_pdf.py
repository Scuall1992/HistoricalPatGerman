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


def replace_smht(s, what):
    for i in what:
        s = s.replace(i, '', 1)
    return s


def read_file_by_lines(filename):
    with open(filename) as rep:
        return rep.read().split("\n")


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument("filename", type=str)

    # file = args.parse_args().filename
    file = 'C:\\patents\\1926\\pat_Patentblatt_192614.pdf'

    try:
        if ".pdf" in file:
            data = extract_text_from_pdf(f'{file}')

            for c in read_file_by_lines("replace_cases"):
                data = data.replace(*c.split(";"))

            res = [(m.start(0), m.end(0)) for m in
                   re.finditer(re_date_of_patent, data)]
            parsed = []

            # replace commas to dots in date
            for i in range(len(res) - 1):
                data = data[:res[i][0]] + data[res[i][0]:res[i][1]].replace(',', '.') + data[res[i][1]:]
                data = data[:res[i + 1][0]] + data[res[i + 1][0]:res[i + 1][1]].replace(',', '.') + data[res[i + 1][1]:]
                parsed.append(data[res[i][1]:res[i + 1][1]])

            for i in range(len(parsed)):
                if parsed[i][0] == " ":
                    parsed[i] = parsed[i][1:]

            with open(f"{file}1.csv", "w", encoding="utf-8") as f:
                f.write("\n".join(parsed))

    except Exception as e:
        print(file, e)
