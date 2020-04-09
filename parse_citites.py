with open("cities.txt", "r", encoding="utf-8") as f:
    lines  = set(f.read().split("\n"))


m = [i for i in  filter(lambda x: "NA" not in x and "c(\"" not in x and ';' in x, lines)]


a = []
for i in m:
    s = i.split(';')

    if s[0] != s[1]:
        a.append(f"{s[1]};{s[0]}")


[print(i) for i in a]
