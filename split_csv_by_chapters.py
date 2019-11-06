import os

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

FOLDER = "C:\\1926"
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
            for i in range(len(anmel) - 1):

                if anmel[i].startswith(", "):
                    anmel[i] = anmel[i][2:]

                if not anmel[i][0].isalpha() and anmel[i][0] != "'":
                    buf.append(anmel[i])
                else:
                    if len(buf) > 0:
                        buf[-1] += f" {anmel[i]}"
                    else:
                        buf.append(f" {anmel[i]}")

            if data.count(a) > 0:
                eterl = data.split(a)[1].split(c)[0]
            elif data.count(a2) > 0:
                eterl = data.split(a2)[1].split(c)[0]
            else:
                eterl = data.split(a3)[1].split(c)[0]

            with open(os.path.join(FOLDER, f"result_{file}"), "w", encoding="utf-8") as r:
                r.write('\n'.join(buf))
                # r.write("-------------------------------------------------\n")
                # r.write(eterl)
