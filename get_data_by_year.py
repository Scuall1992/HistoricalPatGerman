from typing import List, Tuple
import os
import re
import xlsxwriter
from multiprocessing import Process, Pool
from collections import namedtuple

re_id = r'\d{1,2}(\.|,|-)( )?([A-Z]|Sch|St|Sp)(\.|,|-)( )?\d{5,6}(\.|,|-)'
re_date = r"[0-9]{1,2}(\.|,| )( )*[0-9]{1,2}(\.| |,)( )*[0-9]{1,2}[^0-9]"
re_classes = r"(\,|.) "

WEIGHTS = [1.10, 1.40, 2.0]  # for n-gramm compare

CITIES_FILENAME = "cities_1.txt"
NORMAL = 1
INTERNATIONAL = 2
FEW_AUTHORS = 3
KOEF_FOR_N_GRAMM = 0.7

DETERM_LABELS = {
    NORMAL: "NORMAL",
    INTERNATIONAL: "INTERNATIONAL",
    FEW_AUTHORS: "FEW_AUTHORS"
}

folder = "."

# YEARS = map(str, list(range(1907, 1945 + 1)))
YEARS = ["1926", "1927", "1928"]

WEEKS = 100
LINES = 500

REPLACE_CASES = [("2s", "25"), ("2S", "25"), ("Neilin", "Berlin"),
                 ("Nerlin", "Berlin"), ("¬ ", ''), ("Berlm", "Berlin"), ("Beilin", "Berlin")]

Occurence = namedtuple('Occurence', ['score', 'word', 'index', 'city'])
PatentData = namedtuple("PatentData", ["num", "classes", "id", "middle", "date", "city"])


def log(text, DEBUG=False) -> None:
    if DEBUG:
        print(text)


def get_all_cities() -> List[str]:
    with open(CITIES_FILENAME, encoding="utf-8") as f:
        return set([i.strip() for i in f.read().split("\n")])


def delete_symbols_and_split(middle: str, symbols: List[str]) -> List[str]:
    '''Очищаем мидл от лишних символов'''
    table = str.maketrans('', '', symbols)
    return [i for i in [w.translate(table) for w in middle.strip().lower().split(" ")] if len(i) > 0]


def make_n_gramm(s: str, n=3) -> List[str]:
    '''Создать из строки n-граммы по заданному количеству'''
    s = s.lower()
    return [s[i:i + n] for i in range(len(s) - n + 1)]


def evaluate_scores(words: List[str], city: str, n_gramm_min=2, n_gramm_max=5) -> dict:
    '''Делаем подсчет баллов по заданным n-граммам и потом суммируем умножая на веса '''
    score = dict()

    for n in range(n_gramm_min, n_gramm_max):
        summary = 0

        for word in words:

            if word in score:
                if len(score[word]) == 3:
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
            if r == 0:
                continue

            if word in score:
                score[word].append((round(r / summary, 2), word))
            else:
                score[word] = [(round(r / summary, 2), word)]
    return score


def get_n_gramm(middle: str, city: str) -> List[Occurence]:
    '''Считаем совпадения по n-граммам по каждому слову из мидла и потом отдаем с набранными баллами и позицией в строке'''

    res = []
    city = city.lower()
    words = delete_symbols_and_split(middle, ",.")

    score = evaluate_scores(words, city)

    if len(score) > 0:

        for word, v in score.items():

            ind_res = 99 * 99
            try:
                ind_res = middle.lower().index(word)
            except ValueError:
                pass

            res.append(
                Occurence(sum([round(v[j][0] * WEIGHTS[j], 2) for j in range(len(v))]) / len(v), word, ind_res, city))

    return res


def determine_patent(middle: str) -> int:  # 1-normal, 2-international, 3-few_authors
    '''Вернуть тип патента'''
    with open("international_criteria.txt") as f:
        criteria = f.read().split("\n")
        if any([i in middle for i in criteria]):
            return INTERNATIONAL

    mark = "u. "
    i = middle.rfind(mark)
    if i != -1:
        if (i + len(mark)) < len(middle) and not middle[i + len(mark)].isdigit():
            return FEW_AUTHORS

    return NORMAL


def _filter_cities(score_limit: float, middle: str) -> List[Occurence]:
    '''Посчитать n-граммы по каждому городу и отобрать только те, которые выше порога score_limit'''

    n_gramm_by_cities = dict()

    cities = []

    for c in get_all_cities():

        croped = middle.split(",")

        n_gramm_by_cities[c] = get_n_gramm(middle if len(croped) <= 1 else ",".join(croped[1:]), c)

        occurences = list(filter(lambda x: x[0] >= score_limit, n_gramm_by_cities[c]))

        if len(occurences) > 0:
            cities.extend(occurences)

    return cities


def find_next_max(cities: List[Occurence], last_max: float) -> float:
    '''Найти следующий максимум, который меньше last_max'''
    result = 0
    for occur in cities:
        if occur.score < last_max and occur.score > result:
            result = occur.score

    return result


def _get_all_cities_by_max_score(cities: List[Occurence], count: int) -> List[Occurence]:
    '''Забрать только те города баллы которых максимальны'''

    '''Найти max_score'ы'''
    max_score = find_next_max(cities, 9999)
    max_score2 = find_next_max(cities, max_score)

    '''Найти все города которые равны этому индексу'''
    cit = []
    for occur in cities:
        if occur.score == max_score:  # Если соответствует хоть какому-нибудь максимуму. Городов может быть больше 3
            cit.append(occur)

    if len(cit) >= count:
        return cit

    for occur in cities:
        if occur.score == max_score2:  # Если соответствует хоть какому-нибудь максимуму. Городов может быть больше 3
            cit.append(occur)

    return cit


def extract_city(middle: str, count=1) -> str:
    '''Вытащить из мидла город или города '''

    cities = _filter_cities(KOEF_FOR_N_GRAMM, middle)

    cit = _get_all_cities_by_max_score(cities, count)

    min_city_index = 0
    city_res = ""

    # добавить фильтр на максимальное кол-во баллов

    '''Искать то, что максимально близко к началу строки'''
    if len(cit) > 0:
        min_city_index = cit[0].index
        city_res = cit[0].city
        for i in cit:
            if i.index < min_city_index:
                min_city_index = i.index
                city_res = i.city

    # '''Если хотят два, а у нас есть только один'''
    if count == 2 and len(cit) == 1:
        city_res = f"{cit[0].city}, Not recognized"

    # '''Второй город ищем по максимальному кол-ву набранных баллов, но такой, чтобы он не совпадал с первым'''
    elif count == 2 and len(cit) > 1:
        min_city_score2 = cit[0].score
        city_res2 = ""
        for i in cit:
            if i.city != city_res and i.score < min_city_score2:
                min_city_score2 = i.score
                city_res2 = i.city

        city_res = ", ".join([city_res, city_res2])

    log(cit)

    return city_res


def _search_by_regex(pattern: str, line: str) -> str:
    '''Вернуть то, что подходит под паттерн регулярки'''
    mat_id = re.search(pattern, line)
    if mat_id is not None:
        return mat_id.group(0)
    return ""


def _get_middle_from_line(line: str) -> str:
    '''Найти в патенте мидл и вернуть его'''
    return re.sub(re_date, '', re.sub(re_id, '', line))


def _split_middle_on_classes_and_other(middle: str) -> Tuple[str, str]:
    '''Отрезать у мидла класс и вернуть вместе с ним'''
    try:
        return re.subn(re_classes, "$$$$", middle, count=1)[0].split("$$$$")
    except ValueError:
        return ("", "")


def _get_city_by_patent_type(determ: int, middle: str) -> str:
    '''Получить город в зависимости от типа патента'''
    if determ == NORMAL:
        return extract_city(middle)
    elif determ == FEW_AUTHORS:
        return extract_city(middle)
    # else:
    #     return extract_city(middle)


def _delete_all_symbol_from_string(s: str, sym: str) -> str:
    '''Удаляй пока не останется этого символа. Вроде бы сработало бы с одного вызова, но лучше перестраховаться'''
    while sym in s:
        s = s.replace(sym, "")
    return s


def write_to_xlsx(f: str, year: int, res: List[PatentData]) -> None:
    '''Записать данные в ексель'''
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


def _parse_patents_line_by_line(lines: List[str], f: str) -> List[PatentData]:
    '''Распарсить прочитанные строки. Мы разделяем патент на части'''

    res = []
    for line in lines[:-1][:LINES]:

        for repl in REPLACE_CASES:
            line = line.replace(*repl)

        pat_id = _search_by_regex(re_id, line)
        pat_date = _search_by_regex(re_date, line)

        middle = _get_middle_from_line(line)

        classes, middle = _split_middle_on_classes_and_other(middle)

        determ = determine_patent(middle)

        log(f"Middle - {middle} {DETERM_LABELS[determ]}")

        if len(middle) == 0 or determ == INTERNATIONAL:
            continue

        num = re.search(r"\d+", f).group(0)

        middle = _delete_all_symbol_from_string(middle, "-")

        city = _get_city_by_patent_type(determ, middle)

        res.append(PatentData(num, classes, pat_id, middle, pat_date, city.capitalize()))

    return res


def run_parse(FOLDER: str, f: str, year: int) -> None:
    '''Эту функцию можно вызывать из потоков'''
    res = []
    filename_patent = os.path.join(FOLDER, f)
    with open(filename_patent, encoding="utf-8") as ff:
        log(f"Start parse {filename_patent}")

        lines = ff.read().split("\n")

    res = _parse_patents_line_by_line(lines, f)

    write_to_xlsx(f, year, res)

import datetime

if __name__ == '__main__':
    print(datetime.datetime.now())
    parsed_files = os.listdir("parsed")
    with Pool(2) as p:
      args = []
      for y in YEARS:
        if not os.path.exists(os.path.join("parsed", y)):
            os.mkdir(os.path.join("parsed", y))
        FOLDER = os.path.join(folder, y)

        for f in list(filter(lambda x: "result" in x, os.listdir(FOLDER)))[:WEEKS]:
      
                if all([f not in pf for pf in parsed_files]):
                    args.append((FOLDER, f, y))

    #run_parse(*args[0])
      print(datetime.datetime.now())
      p.starmap(run_parse, args)

