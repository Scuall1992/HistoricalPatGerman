import os
import re
import argparse


def replace_smht(s, what):
    for i in what:
        s = s.replace(i, '', 1)
    return s


LENGTH_OF_LINE = 45  # if less, then add to previous line

args = argparse.ArgumentParser()
args.add_argument("filename", type=str)

FOLDER = args.parse_args().filename

lines = []

for i in os.listdir(FOLDER):
    if ".csv" in i:
        with open(os.path.join(FOLDER, i), encoding="utf-8") as f:
            lines.clear()
            data = f.read().split("\n")

            for j in range(len(data) - 1):

                if len(data[j]) < LENGTH_OF_LINE and j > 0:
                    lines[-1] += f" {data[j]}"
                else:
                    lines.append(data[j])

        with open(os.path.join(FOLDER, i), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

a = ["Erteilungen.", "Erteilungen/", "Versagungen.", "Erteilungen*)"]

b = ["Anmeldungen.", "Anmelllungen."]

# c = "Löschungen."

files = []

for i in os.listdir(FOLDER):
    if ".csv" in i:
        with open(os.path.join(FOLDER, i), encoding="utf-8") as f:
            data = f.read()

        if any([data.count(i) == 1 for i in a]) and any([data.count(i) == 1 for i in b]):
            files.append(i)

with open("replace_cases", encoding="utf-8") as g:
    cases = g.read().split("\n")

for file in files:
    with open(os.path.join(FOLDER, file), encoding="utf-8") as g:
        data = g.read()

        for j in cases:
            data = data.replace(*j.split(";"))

        for case in b:
            if data.count(case) > 0:
                anmel = data.split(case)[0]
                break

        anmel = anmel.split("\n")
        buf = []

        # join every line startswith alpha to previous
        for i in range(len(anmel) - 1):
            anmel[i] = anmel[i].lstrip()

            if anmel[i].startswith(", "):
                anmel[i] = anmel[i][2:]

            if not anmel[i][0].isalpha() and anmel[i][0] != "'":
                buf.append(anmel[i])
            else:
                if len(buf) > 0 and not re.search(r'[0-9]{3}(\.|,| )', anmel[i]):
                    buf[-1] += f" {anmel[i]}"
                else:
                    buf.append(f" {anmel[i]}")

        # join list in string
        buf = "\n".join(buf)

        # delete eterlungen from file
        for case in a:
            if buf.count(case) > 0:
                res = buf.split(case)[0]
                break

        lines = res.split("\n")
        res = []
        for i in lines:
            r = i
            if i.startswith(". "):
                r = i.replace(". ", "", 1)
            res.append(r)
        res = "\n".join(res)

        # concat all 6-digit numbers and replace dot to comma
        buf = [(m.start(0), m.end(0)) for m in
               re.finditer(r"[0-9]{2,3} [0-9]{3}(\.|,| )", res)]
        for i in buf[::-1]:
            res = res[:i[0]] + res[i[0]: i[1]].replace(" ", "", 1).replace(".", ',').replace(" ", ',') + res[i[1]:]

        # replace dot to comma in all 5-6 digit numbers with
        buf = [(m.start(0), m.end(0)) for m in
               re.finditer(r"[0-9]{5,6}.", res)]
        for i in buf[::-1]:
            res = res[:i[0]] + res[i[0]: i[1]].replace(".", ',') + res[i[1]:]

        with open(os.path.join(FOLDER, f"result_{file}"), "w", encoding="utf-8") as r:
            r.write(res)
