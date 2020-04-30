import os

import argparse
args = argparse.ArgumentParser()
args.add_argument("filename", type=str)
#
FOLDER = args.parse_args().filename

lines = []

for i in os.listdir(FOLDER):
    if ".csv" in i:
        with open(os.path.join(FOLDER, i), encoding="utf-8") as f:
            lines.clear()
            data = f.read().split("\n")

            for j in range(len(data)-1):

                if len(data[j]) < 45 and j > 0:
                    lines[-1] += f" {data[j]}"
                else:
                    lines.append(data[j])

        with open(os.path.join(FOLDER, i), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
