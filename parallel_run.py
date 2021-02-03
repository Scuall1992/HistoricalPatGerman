from multiprocessing import Process, Pool
import os
import argparse
args = argparse.ArgumentParser()
args.add_argument("type_parse", type=int)
type_parse = args.parse_args().type_parse

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))


def run_script(filename):
    os.system(f"python3 {os.path.join(BASE_FOLDER, 'parse_one_pdf.py')} {filename}")


def run_script_folder(filename):
    os.system(f"python3 {os.path.join(BASE_FOLDER, 'clean_files.py')} {filename}")


if __name__ == '__main__':
    FOLDER = "."
    years = [f"{i}" for i in range(1940, 1946)]

    if type_parse <= 0:
        for y in years:
            [run_script(os.path.join(FOLDER, y, i)) for i in os.listdir(os.path.join(FOLDER, y)) if i.endswith('.pdf')]
    else:
        for y in years:
            run_script_folder(os.path.join(FOLDER, y))
