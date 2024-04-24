import csv


def read_csv(file_name):
    with open(file_name, newline='', encoding="utf-8") as file:
        reader = csv.DictReader(file)
        reader_list = [{row["Factor_name"]: row["Value"]} for row in reader]

        reader_dict = dict()
        for el in reader_list:
            reader_dict.update(el)

        factors_dict = dict()
        factors_dict["req_nav_back"] = int(reader_dict["Необходимость наведения в зад. полусферу"])
        factors_dict["pref_nav_back"] = int(reader_dict["Предпочтительно наведение в зад. полусферу"])
        factors_dict["nav_min"] = int(reader_dict["Требование наведения за мин. время"])
        factors_dict["stealth"] = int(reader_dict["Требование к скрытности"])
        factors_dict["nav_type"] = reader_dict["Тип наведения"].upper()
        factors_dict["half_sphere"] = reader_dict["Нахождение в полусфере относительно цели"].upper()
        factors_dict["vel_pryam"] = int(reader_dict["Реализация по скорости «Прямого метода»"])
        factors_dict["vel_man"] = int(reader_dict["Реализация по скорости «Метода манёвра»"])
        factors_dict["vel_pereh"] = int(reader_dict["Реализация по скорости «Метода перехвата»"])
        factors_dict["tr_pryam"] = int(reader_dict["Реализация траектории «Прямого метода»"])
        factors_dict["tr_man"] = int(reader_dict["Реализация траектории «Метода манёвра»"])
        factors_dict["tr_pereh"] = int(reader_dict["Реализация траектории «Метода перехвата»"])
        factors_dict["top_pryam"] = int(reader_dict["Реализация по запасу топлива «Прямого метода»"])
        factors_dict["top_man"] = int(reader_dict["Реализация по запасу топлива «Метода манёвра»"])
        factors_dict["top_pereh"] = int(reader_dict["Реализация по запасу топлива «Метода перехвата»"])

        return factors_dict


def process(factors_dict):
    methods_dict = {"прямой": True, "манёвр": True, "перехват": True, "невозможно": False}

    # правило 1
    if factors_dict["nav_type"] == "РАД" and \
            factors_dict["stealth"] == 1:
        methods_dict["невозможно"] = True
        print("ERROR: невозможно выбрать метод наведения "
              "(тип наведения: РАД, требование к скрытности: 1)")
        return "невозможно"

    # правило 2
    if factors_dict["nav_type"] == "ТЕП" and \
            (factors_dict["req_nav_back"] == 1 or
             factors_dict["pref_nav_back"] == 1):
        methods_dict["невозможно"] = True
        print("ERROR: невозможно выбрать метод наведения "
              "(тип наведения: ТЕП, необходимо или предпочтительно наведение в заднюю полусферу: 1)")
        return "невозможно"

    # правило 3
    if (factors_dict["nav_type"] == "ТЕП" or factors_dict["stealth"] == 1)\
            and (factors_dict["half_sphere"] == "ПЕР"):
        methods_dict["перехват"] = False

    # правило 4
    if factors_dict["vel_pryam"] == 0 or \
            factors_dict["tr_pryam"] == 0 or \
            factors_dict["top_pryam"] == 0:
        methods_dict["прямой"] = False

    # правило 5
    if factors_dict["vel_pereh"] == 0 or \
            factors_dict["tr_pereh"] == 0 or \
            factors_dict["top_pereh"] == 0:
        methods_dict["перехват"] = False

    # правило 6
    if factors_dict["vel_man"] == 0 or \
            factors_dict["tr_man"] == 0 or \
            factors_dict["top_man"] == 0:
        methods_dict["манёвр"] = False

    # правило 7
    if factors_dict["pref_nav_back"] == 1 and \
            (methods_dict["манёвр"] or methods_dict["прямой"]):
        methods_dict["перехват"] = False

    # правило 8
    if not methods_dict["манёвр"] and not methods_dict["прямой"] and not methods_dict["перехват"]:
        methods_dict["невозможно"] = True
        print("ERROR: ни один из методов наведения не реализуем")
        return "невозможно"

    # правило 9
    if methods_dict["перехват"]:
        methods_dict["перехват"] = True
        return "перехват"

    # правило 10
    if methods_dict["прямой"]:
        methods_dict["прямой"] = True
        return "прямой"

    # правило 11
    if methods_dict["манёвр"]:
        methods_dict["манёвр"] = True
        return "манёвр"


if __name__ == "__main__":
    file_name = "input.csv"
    _factors_dict = read_csv(file_name)

    # обрабатываем
    method_name = process(_factors_dict)

    if method_name == "невозможно":
        print("Входные данные содержат ошибку и нельзя выбрать ни один из методов наведения")
    elif method_name == "перехват":
        print("Исходя из переданного ситуационного вектора был выбран метод парехвата")
    elif method_name == "прямой":
        print("Исходя из переданного ситуационного вектора был выбран прямой метод наведения")
    elif method_name == "манёвр":
        print("Исходя из переданного ситуационного вектора был выбран метод манёвра")
