import os
import re

a = "Erteilungen."
a2 = "Erteilungen/"
a3 = "Versagungen."
b = "Anmeldungen."
b2 = "Anmelllungen."
c = "Löschungen."


def replace_smht(s, what):
    for i in what:
        s = s.replace(i, '', 1)
    return s


with open("replace_cases", encoding="utf-8") as g:
    cases = g.read().split("\n")

FOLDER = "C:\\19262"
with open("files.txt", encoding="utf-8") as f:
    for file in f.read().split():
        with open(os.path.join(FOLDER, file), encoding="utf-8") as g:
            data = g.read()

            if data.count(b) > 0:
                anmel = data.split(b)[0]
            elif data.count(b2) > 0:
                anmel = data.split(b2)[0]

            for j in cases:
                anmel = anmel.replace(*j.split(";"))

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
            if buf.count(a) > 0:
                res = buf.split(a)[0]
            elif buf.count(a2) > 0:
                res = buf.split(a2)[0]
            else:
                res = buf.split(a3)[0]

            # run every replace case by lines
            with open("replace_cases") as rep:
                cases = rep.read().split("\n")

                for c in cases:
                    res = res.replace(*c.split(";"))

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
                res = res[:i[0]] + res[i[0]: i[1]].replace(" ", "",1).replace(".", ',').replace(" ", ',') + res[i[1]:]

            # replace dot to comma in all 5-6 digit numbers with
            buf = [(m.start(0), m.end(0)) for m in
                   re.finditer(r"[0-9]{5,6}.", res)]
            for i in buf[::-1]:
                res = res[:i[0]] + res[i[0]: i[1]].replace(".", ',') + res[i[1]:]

            # if data.count(a) > 0:
            #     eterl = data.split(a)[1].split(c)[0]
            # elif data.count(a2) > 0:
            #     eterl = data.split(a2)[1].split(c)[0]
            # else:
            #     eterl = data.split(a3)[1].split(c)[0]

            with open(os.path.join(FOLDER, f"result_{file}"), "w", encoding="utf-8") as r:
                r.write(res)
