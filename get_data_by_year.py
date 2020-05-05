import os
import re
import xlsxwriter

CITIES_FILENAME = "cities_1.txt"
NORMAL = 1
INTERNATIONAL = 2
FEW_AUTHORS = 3


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

        for k, v in balls.items():

            ind_res = 99*99
            try:
                ind_res = middle.lower().index(k)
            except ValueError:
                pass

            res.extend([(sum([round(v[j][0] * weights[j], 2) for j in range(len(v))]) / len(v), k, ind_res)])

    return res


# get_n_gramm(
#     "Paris; Bertr,: K. Osius u, Nr. A. Zehden, Pat.-Anwälte, Berlin SW11. Entstaubungsanlage für Kohle und andere körnige Stoffe.",
#     "Par-ris")

def determine_patent(middle):  # 1-normal, 2-international, 3-few_authors
    res = NORMAL

    with open("international_criteria.txt") as f:
        criteria = f.read().split("\n")
        if any([i in middle for i in criteria]):
            res = INTERNATIONAL

    return res


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


def extract_city(middle):
    n_gramm_by_cities = dict()

    cities = []

    while "-" in middle:
        middle = middle.replace("-", "")

    for c in get_all_cities():

        croped = middle.split(",")

        n_gramm_by_cities[c] = get_n_gramm(middle if len(croped) <= 1 else ",".join(croped[1:]), c)

        occurences = list(filter(lambda x: x[0] >= 0.8, n_gramm_by_cities[c]))

        if len(occurences) > 0:
            cities.append((c, occurences))

    max_index = 0

    for city, occur in cities:
        for j in occur:
            if j[0] > max_index:
                max_index = j[0]

    cit = []
    for city, occur in cities:
        for j in occur:
            if j[0] == max_index:
                cit.append((city, j[2]))

    min_city = cit[0][1]
    city_res = cit[0][0]
    for i in cit:
        if i[1] < min_city:
            min_city = i[1]
            city_res = i[0]

    return [num, classes, pat_id, middle, pat_date, city_res]


re_id = r'\d{1,2}(\.|,|-)( )?([A-Z]|Sch|St|Sp)(\.|,|-)( )?\d{5,6}(\.|,|-)'
re_date = r"[0-9]{1,2}(\.|,| )( )*[0-9]{1,2}(\.| |,)( )*[0-9]{1,2}[^0-9]"

folder = "C:\\patents"

# years = map(str, list(range(1925, 1928 + 1)))
years = ["1926"]

WEEKS = 2
LINES = 30


for y in years:
    FOLDER = os.path.join(folder, y)

    for f in list(filter(lambda x: "result" in x, os.listdir(FOLDER)))[:WEEKS]:
        res = []
        with open(os.path.join(FOLDER, f), encoding="utf-8") as ff:
            lines = ff.read().split("\n")

            for line in lines[:-1][:LINES]:
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

                if determine_patent(middle) != NORMAL:
                    continue

                re_classes = r"(\,|.) "

                try:
                    s = re.subn(re_classes, "$$$$", middle, count=1)
                    classes, middle = s[0].split("$$$$")
                except ValueError as e:
                    pass

                num = re.search(r"\d+", f).group(0)

                if len(middle) == 0:
                    continue

                res.append(extract_city(middle))

        # Create a workbook and add a worksheet.
        workbook = xlsxwriter.Workbook(f'parsed\\{f}_parsed.xlsx')

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
