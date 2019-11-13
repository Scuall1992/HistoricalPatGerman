import os

# a = "ilungen"
a = "Erteilungen."
a2 = "Erteilungen/"
a3 = "Versagungen."
b = "Anmeldungen."
b2 = "Anmelllungen."
c = "Löschungen."
files = []
FOLDER = "C:\\19262"

for i in os.listdir(FOLDER):
    if ".csv" in i:
        with open(os.path.join(FOLDER, i), encoding="utf-8") as f:
            data = f.read()

        if (data.count(a) == 1 or data.count(a2) == 1 or data.count(a3) == 1) and (data.count(b) == 1 or data.count(b2) == 1 ):
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
