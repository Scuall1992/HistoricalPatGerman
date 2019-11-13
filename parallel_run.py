from multiprocessing import Process
import os


def run_script(filename):
    os.system(f"python C:\\Users\\scual\\PycharmProjects\\untitled\\parse_one_pdf.py {filename}")


# if __name__ == '__main__':
#     FOLDER = "C:\\pat"
#     p = Pool(30)
#     p.map(run_script, [os.path.join(FOLDER, i) for i in os.listdir(FOLDER)])

if __name__ == '__main__':
    FOLDER = "C:\\19262"
    for i in os.listdir(FOLDER):
        if ".pdf" in i:
            Process(target=run_script, args=(os.path.join(FOLDER, i),)).start()

