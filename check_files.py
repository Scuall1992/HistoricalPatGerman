import os

# a = "ilungen"
a = ["Erteilungen.", "Erteilungen/", "Versagungen.", "Erteilungen*)"]


b = ["Anmeldungen.", "Anmelllungen."]

c = "Löschungen."
files = []



import argparse
args = argparse.ArgumentParser()
args.add_argument("filename", type=str)
#
FOLDER = args.parse_args().filename


for i in os.listdir(FOLDER):
    if ".csv" in i:
        with open(os.path.join(FOLDER, i), encoding="utf-8") as f:
            data = f.read()

        if any([data.count(i) == 1 for i in a]) and any([data.count(i) == 1 for i in b]):
            files.append(i)
        # if data.count(a) == 1 and data.count(b) == 1 and data.count(c) >= 1:
        #     files.append(i)

with open("files.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(files))

# [print(i) for i in files]
# print(len(files))
# print(len(files))
# count = 0
# for i in os.listdir("."):
#     if ".csv" in i:
#         with open(i) as f:
#             data = f.read()

#             if a not in data or b not in data:
#                 count += 1

# print(count, len(os.listdir("."))-1)

# count = 0
# for i in os.listdir("."):
#     if ".csv" in i:
#         with open(i) as f:
#             data = f.read()

#             if a not in data:
#                 count += 1

# print(count, len(os.listdir("."))-1)
