import os
import re
import xlsxwriter
from multiprocessing import Process, Pool

CITIES_FILENAME = "cities_1.txt"
NORMAL = 1
INTERNATIONAL = 2
FEW_AUTHORS = 3  

determ_labels = {
    NORMAL : "NORMAL",
    INTERNATIONAL: "INTERNATIONAL",
    FEW_AUTHORS: "FEW_AUTHORS"
}




re_id = r'\d{1,2}(\.|,|-)( )?([A-Z]|Sch|St|Sp)(\.|,|-)( )?\d{5,6}(\.|,|-)'
re_date = r"[0-9]{1,2}(\.|,| )( )*[0-9]{1,2}(\.| |,)( )*[0-9]{1,2}[^0-9]"

folder = "."

#years = map(str, list(range(1907, 1945 + 1)))
years = ["1926"]

WEEKS = 100
LINES = 50

replace_cases = [("2s", "25"), ("2S", "25"), ("Neilin", "Berlin"),
                 ("Nerlin", "Berlin"), ("¬ ", ''), ("Berlm", "Berlin")]


def log(text, DEBUG=False):
    if DEBUG:
        print(text)


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

    for n in range(2, 5): #n-gramm length
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

            ind_res = 99 * 99
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

    with open("international_criteria.txt") as f:
        criteria = f.read().split("\n")
        if any([i in middle for i in criteria]):
            return INTERNATIONAL

    mark = "u. "
    i = middle.rfind(mark)
    if i != -1:
        if (i+len(mark)) < len(middle) and not middle[i+len(mark)].isdigit():
            return FEW_AUTHORS

    return NORMAL


def extract_city(middle, count=1):
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

    min_city = 0
    city_res = ""
    if len(cit) > 0 and len(cit[0]) > 1:
        min_city = cit[0][1]
        city_res = cit[0][0]
        for i in cit:
            if i[1] < min_city:
                min_city = i[1]
                city_res = i[0]

    if count == 2 and len(cit) > 1:
        min_city2 = cit[0][1]
        city_res2 = cit[0][0]
        for i in cit:
            if i[1] != min_city and i[1] < min_city2:
                min_city2 = i[1]
                city_res2 = i[0]

        city_res = ", ".join([city_res, city_res2])
    log(cit)
    # return [num, classes, pat_id, middle, pat_date, city_res]
    return city_res

def write_to_xlsx(f, year, res):
    # Create a workbook and add a worksheet.
    log(f"Write to file {f}_parsed.xlsx")
    workbook = xlsxwriter.Workbook(os.path.join("parsed", year, f"{f}_parsed.xlsx"))

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


def _search_by_regex(pattern, line):
    mat_id = re.search(pattern, line)
    if mat_id is not None:
        return mat_id.group(0)
    return ""

def run_parse(FOLDER, f, year):
    res = []
    filename_patent = os.path.join(FOLDER, f)
    with open(filename_patent, encoding="utf-8") as ff:
        log(f"Start parse {filename_patent}")

        lines = ff.read().split("\n")

    for line in lines[:-1][:LINES]:
        
        for repl in replace_cases:
            line = line.replace(*repl)

        pat_id = _search_by_regex(re_id, line)
        pat_date = _search_by_regex(re_date, line)

        middle = re.sub(re_date, '', re.sub(re_id, '', line))
        
        determ = determine_patent(middle)

        #log(f"Line {line}")
        log(f"Middle - {middle} {determ_labels[determ]}")

        re_classes = r"(\,|.) "
        try:
            s = re.subn(re_classes, "$$$$", middle, count=1)
            classes, middle = s[0].split("$$$$")
        except ValueError as e:
            pass

        if len(middle) == 0:
            continue

        num = re.search(r"\d+", f).group(0)

        if determ == NORMAL:               
            city = extract_city(middle)
        elif determ == FEW_AUTHORS:
            city = extract_city(middle, 2)

        res.append([num, classes, pat_id, middle, pat_date, city])

    write_to_xlsx(f, year, res)




if __name__ == '__main__':
    parsed_files = os.listdir("parsed")
    # with Pool(10) as p:
    args = []
    for y in years:
        if not os.path.exists(os.path.join("parsed", y)):
            os.mkdir(os.path.join("parsed", y))
        FOLDER = os.path.join(folder, y)

        for f in list(filter(lambda x: "result" in x, os.listdir(FOLDER)))[:WEEKS]:
            if "192615" in f:

                if all([f not in pf for pf in parsed_files]):

                    args.append((FOLDER, f, y))

    run_parse(*args[0])
    # p.starmap(run_parse, args)
