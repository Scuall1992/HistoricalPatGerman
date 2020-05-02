import os
import re

CITIES_FILENAME = "cities_1.txt"


def get_all_cities():
    with open(CITIES_FILENAME, encoding="utf-8") as f:
        return set([i.strip() for i in f.read().split("\n")])


def delete_symbols_and_split(middle, symbols):
    table = str.maketrans('', '', symbols)
    return [i for i in [w.translate(table) for w in middle.strip().lower().split(" ")] if len(i) > 0]


def make_n_gramm(s, n=3):
    s = s.lower()
    return [s[i:i + n] for i in range(len(s) - n + 1)]


def get_n_gramm(middle, city):
    res = []
    b = len(city)
    city = city.lower()
    words = delete_symbols_and_split(middle, ",.")

    balls = dict()

    for n in range(2, 5):
        summary = 0

        for word in words:

            if word in balls:
                if len(balls[word]) == 3:
                    continue

            c = make_n_gramm(city, n)
            k = make_n_gramm(word, n)

            summary = len(c) + len(k)
            if summary == 0:
                continue
            r = 0
            for i in c:
                if i in k:
                    r += 2

            if word in balls:
                balls[word].append((round(r / summary, 2), word))
            else:
                balls[word] = [(round(r / summary, 2), word)]

    weights = [1.50, 1.80, 2.0]

    if len(balls) > 0:
        res.extend(
            [(sum([round(v[j][0] * weights[j], 2) for j in range(len(v))]) / len(v), k) for k, v in balls.items()])

    return res


# get_n_gramm(
#     "Paris; Bertr,: K. Osius u, Nr. A. Zehden, Pat.-Anwälte, Berlin SW11. Entstaubungsanlage für Kohle und andere körnige Stoffe.",
#     "Par-ris")


def filter_cities(cities_with_word):
    buf = dict()

    for i in cities_with_word:
        if i[1][0][1] in buf:
            buf[i[1][0][1]].append((i[0], *i[1][0]))
        else:
            buf[i[1][0][1]] = [(i[0], *i[1][0])]

    res = []

    for k, v in buf.items():
        if len(v) <= 1:
            res.extend(v)
        else:
            m = max(v, key=lambda x: x[1])

            res.extend(list(filter(lambda x: x == m, v)))

    return res


re_id = r'\d{1,2}(\.|,|-)( )?([A-Z]|Sch|St|Sp)(\.|,|-)( )?\d{5,6}(\.|,|-)'
re_date = r"[0-9]{1,2}(\.|,| )( )*[0-9]{1,2}(\.| |,)( )*[0-9]{1,2}[^0-9]"

res = []

folder = "C:\\patents"

# years = map(str, list(range(1925, 1928 + 1)))
years = ["1925"]

all_cities = get_all_cities()

for y in years:
    FOLDER = os.path.join(folder, y)

    for f in list(filter(lambda x: "result" in x, os.listdir(FOLDER)))[:1]:
        with open(os.path.join(FOLDER, f), encoding="utf-8") as ff:
            lines = ff.read().split("\n")

            for line in lines[:-1][:50]:
                line = line.replace("2s", "25").replace("2S", "25")

                pat_id = ""
                pat_date = ""

                mat_id = re.search(re_id, line)
                if mat_id is not None:
                    pat_id = mat_id.group(0)

                mat_date = re.search(re_date, line)
                if mat_date is not None:
                    pat_date = mat_date.group(0)

                middle = re.sub(re_date, '', re.sub(re_id, '', line))

                re_classes = r"(\,|.) "

                try:
                    s = re.subn(re_classes, "$$$$", middle, count=1)
                    classes, middle = s[0].split("$$$$")
                except ValueError as e:
                    pass

                num = re.search(r"\d+", f).group(0)

                cities = []

                if len(middle) == 0:
                    continue

                n_gramm_by_cities = dict()

                for c in all_cities:

                    croped = middle.split(",")

                    n_gramm_by_cities[c] = get_n_gramm(middle if len(croped) <= 1 else ",".join(croped[1:3]), c)

                    occurences = list(filter(lambda x: x[0] >= 0.6, n_gramm_by_cities[c]))
                    # n_gramm = get_n_gramm(middle if len(croped) <= 1 else ",".join(croped[1:]) , c)

                    if len(occurences) > 0:
                        cities.append((c, occurences))

                if len(cities) > 1:
                    # если совпадение прошло по одному и тому же слову, то надо выбрать с максимальным коэфициентом
                    city_str = ",".join([i[0] for i in filter_cities(cities)])
                else:
                    city_str = ",".join([i[0] for i in cities])

                if city_str.count(',') > 1:
                    cities = city_str.split(',')

                    i_min = 0
                    min = ""

                    new_middle = middle.lower()
                    for c in cities:
                        n = max([i[0] for i in n_gramm_by_cities[c]])
                        m = ""
                        for a in n_gramm_by_cities[c]:
                            if n == a[0]:
                                m = a[1]
                                break
                        fff = new_middle.find(m)

                        if fff < i_min:
                            i_min = fff
                            min = m

                else:
                    min = city_str

                res.append([num, classes, pat_id, middle, pat_date, min])

import xlsxwriter

# Create a workbook and add a worksheet.
workbook = xlsxwriter.Workbook('patent.xlsx')

worksheet = workbook.add_worksheet()

# Start from the first cell. Rows and columns are zero indexed.
row = 0

# Iterate over the data and write it out row by row.
for i in res:
    col = 0
    for j in i:
        worksheet.write(row, col, j)
        col += 1

    row += 1

workbook.close()
