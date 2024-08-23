def weather_judge_page(current_json):
    judge_key = False
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Beijing ")
    if len(outs) > 0:
        judge_key = True
    return {"1": judge_key, "complete": judge_key}


def weather_1(current_json):
    judge_key = False
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Beijing ")
    if len(outs) > 0:
        judge_key = True
    return {"judge_page": True, "1": judge_key, "complete": judge_key}


def weather_2(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Beijing ")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature, Today")
    cnt = 0
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if cnt == 1:
                    key = key.split("Daytime: ")[-1]
                    key = key.split("Nighttime: ")[0]
                    key = key.split(",")[1]
                    key = key.lstrip()
                    key_1 = key.split("\u202f")[0]
                    key_2 = key.split("\u202f")[1]
                    key = key_1 + " " + key_2
                    return {"judge_page": True, "judge_key": key}
                if cnt >= 1:
                    cnt += 1
                if ("Temperature, Today" in key):
                    cnt += 1
    return {"judge_page": True, "judge_key": "Not found"}


def weather_3(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Shanghai ")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature, Today")
    cnt = 0
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if ("Temperature, Today" in key):
                    key = key.split("Daytime: ")[-1]
                    key_day = key.split("Nighttime: ")[0]
                    key_day = key_day.split(",")[0]
                    key_day = key_day.lstrip()
                    key_night = key.split("Nighttime: ")[-1]
                    key_night = key_night.split(",")[0]
                    key_night = key_night.lstrip()
                    return {"judge_page": True, "judge_day_weather": key_day, "judge_night_weather": key_night}
    return {"judge_page": True, "judge_day_weather": "Not found", "judge_night_weather": "Not found"}


def weather_4(current_json):
    judge_key = False
    outs = find_subtrees_of_parents_with_key(current_json, "Shanghai ")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "0 min. ago 0 min. ago ")
    if len(outs) > 0:
        judge_key = True
    return {"1": judge_key, "complete": judge_key}


def weather_5(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Shanghai ")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Sunset at ")
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if ("Sunset at " in key):
                    key = key.split("Sunset at ")[-1]
                    key = key.split(",")[0]
                    key = key.lstrip()
                    return {"judge_page": True, "judge_key": key}
    return {"judge_page": True, "judge_key": "Not found"}


def weather_6(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "3/16")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Sun & moon, ")
    count = 0
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if ("Sunrise at ") in key:
                    count += 1
                if count == 2:
                    key = key.split("Sunrise at ")[-1]
                    key = key.split(",")[0]
                    key = key.lstrip()
                    return {"judge_page": True, "judge_key": key}
    return {"judge_page": True, "judge_key": "Not found"}


def weather_7(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Beijing")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Air quality ")
    count = 0
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if count == 2:
                    key = key.split(",")[-1]
                    key = key.lstrip()
                    key = key.rstrip()
                    return {"judge_page": True, "judge_key": key}
                if count >= 1:
                    count += 1
                if ("Air quality ") in key:
                    count += 1
    return {"judge_page": True, "judge_key": "Not found"}


def weather_8(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature, Today")
    cnt = 0
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if cnt == 1:
                    key = key.split("Daytime: ")[-1]
                    key = key.split("Nighttime: ")[0]
                    key = key.split(",")[1]
                    key = key.lstrip()
                    key_1 = key.split("\u202f")[0]
                    key_2 = key.split("\u202f")[1]
                    key = key_1 + " " + key_2
                    return {"judge_page": True, "judge_key": key}
                if cnt >= 1:
                    cnt += 1
                if ("Temperature, Today" in key):
                    cnt += 1
    return {"judge_page": True, "judge_key": "Not found"}


def weather_9(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature, Today")
    cnt = 0
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if ("Temperature, Today" in key):
                    key = key.split("Daytime: ")[-1]
                    key_day = key.split("Nighttime: ")[0]
                    key_day = key_day.split(",")[0]
                    key_day = key_day.lstrip()
                    key_night = key.split("Nighttime: ")[-1]
                    key_night = key_night.split(",")[0]
                    key_night = key_night.lstrip()
                    return {"judge_page": True, "judge_day_weather": key_day, "judge_night_weather": key_night}
    return {"judge_page": True, "judge_day_weather": "Not found", "judge_night_weather": "Not found"}


def weather_10(current_json):
    judge_key = False
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "0 min. ago 0 min. ago ")
    if len(outs) > 0:
        judge_key = True
    return {"1": judge_key, "complete": judge_key}


def weather_11(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Sunset at ")
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if ("Sunset at " in key):
                    key = key.split("Sunset at ")[-1]
                    key = key.split(",")[0]
                    key = key.lstrip()
                    return {"judge_page": True, "judge_key": key}
    return {"judge_page": True, "judge_key": "Not found"}


def weather_12(current_json):
    outs = find_subtrees_of_parents_with_key(current_json, "Temperature")
    if len(outs) == 0:
        return {"judge_page": False}
    outs = find_subtrees_of_parents_with_key(current_json, "Air quality ")
    count = 0
    for out in outs:
        out = out.values()
        for single_out in out:
            for key, value in single_out.items():
                if count == 2:
                    key = key.split(",")[-1]
                    key = key.lstrip()
                    key = key.rstrip()
                    return {"judge_page": True, "judge_key": key}
                if count >= 1:
                    count += 1
                if ("Air quality ") in key:
                    count += 1
    return {"judge_page": True, "judge_key": "Not found"}
