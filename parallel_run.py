from multiprocessing import Process
import os


def run_script(filename):
    os.system(f"python C:\\Users\\Maria\\PycharmProjects\\untitled\\parse_one_pdf.py {filename}")


def run_script_folder(filename):
    os.system(f"python C:\\Users\\Maria\\PycharmProjects\\untitled\\clean_csv.py {filename}")
    os.system(f"python C:\\Users\\Maria\\PycharmProjects\\untitled\\check_files.py {filename}")
    os.system(f"python C:\\Users\\Maria\\PycharmProjects\\untitled\\split_csv_by_chapters.py {filename}")


# if __name__ == '__main__':
#     FOLDER = "C:\\pat"
#     p = Pool(30)
#     p.map(run_script, [os.path.join(FOLDER, i) for i in os.listdir(FOLDER)])

if __name__ == '__main__':
    FOLDER = "C:\\patents\\"

    # years = [str(i) for i in list(range(1907, 1910))]
    years = map(str, list(range(1907, 1946)))

    for y in years:
        folder = FOLDER + y
        # for i in os.listdir(folder):
        #     if ".pdf" in i and ".csv" not in i:
        run_script_folder(folder)



