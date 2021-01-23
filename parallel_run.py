from multiprocessing import Process, Pool
import os

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


def run_script(filename):
    os.system(f"pypy3 {os.path.join(BASE_FOLDER, 'parse_one_pdf.py')} {filename}")


def run_script_folder(filename):
    os.system(f"pypy3 {os.path.join(BASE_FOLDER, 'clean_files.py')} {filename}")


if __name__ == '__main__':
    FOLDER = "."
    years = ["1929", "1930", "1931", "1932", "1933", "1934", "1935", "1936"]

    # for y in years:
    #     [run_script(os.path.join(FOLDER, y, i)) for i in os.listdir(os.path.join(FOLDER, y)) if i.endswith('.pdf')]

    for y in years:
        run_script_folder(os.path.join(FOLDER, y))
