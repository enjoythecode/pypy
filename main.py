from classes import *
from defs import *
from helpers import parse

test_report = Analyzer()
current = Analyzer()

COULD_NOT_FIND = []

def parse(str):
    parts = str.split("+")
    result = []
    for part in parts:
        stripped = part.strip(" ")

        voidable = part[0] == "("

        stripped = stripped.strip("(")
        stripped = stripped.strip(")")
        stripped = stripped.strip(" ")

        first_space = stripped.find(" ")
        assert first_space > -1, f"could not find space in {stripped}"

        number = float(stripped[:first_space])
        text = stripped[first_space+1:]

        prio = 0
        if text.find("@") > -1:
            prio = int(text.split("@")[1].strip(" "))
            text = text.split("@")[0].strip(" ")

        if text.upper() not in T:
            print("could not find in T: ", text.upper())
            COULD_NOT_FIND.append(text.upper())
        else:
            result.append(Rate(T[text.upper()], number, prio, voidable))
        
    return result



automation_science = Line("Auto Science", "",
    inputs = parse("480 Native Flora + 41.2 Log + 288 Ash + 384 Stone Brick + 264 Iron Plate + 72 Copper Plate + 2.02 MW"),
    outputs = parse("48 Automation Science Pack"),
    registers = [test_report, current])

optical_fiber = Line("Optical Fiber", """
inR0c+YKKMrPSk0uCUhMT+Uy0DPVs9Az4OLiAgAAAP//1ZdNb+IwEIb/i88kIhQWyqlaaSvtoRJa9bJa9TB2JsHCH5HjlKaI/76TBFZs+GjTShRycux5PY/tmbG8YsIaj8Y/lhmyKftNpuGDjVGFJIgL4aU1j8AVsh5LCxmTzU18E4+Gg5gP+HCYTJCPJuNxBMNb4BHnt32ylDQrWf70qEObeSlABYnk6GjMgK48DUbU3jhn0xXDlwxMjOTAuwJ7TEmzyNn0z4ql1sb5sdlA26KaoB8Oo2/0jalLpdZJP9fUu+619IYnGAgLXpp0V/6GbIHPCtwHhMJmGX5IqCCm7SClw66yd3u6V3SkoZHeWY7mFU0XV6mCPO/A1zgDra2R0EWiraIoCWp/HfgysqdgCTi4DiqNCrR870Y0gKIEQ45AUH4clz31mEMhM2zCumnTHL/qxl5kU15IX9L4j7oRQuGtBk8hkYDw1pWBXvQjMkwKVGQ2s0t0ISpKcidFJaUh+YLx90KqKiTyGglNlc3/0sxDWndrSnZVkZlCqR7LC546W2SnMvON9bQy7UKW0/w/g5NgfL2K6jjb7Hvpfkb66NP0ezWnTd9wWVW+ktklgf9f88646aNPs7eKaJs94Q5r6Eva700tDgpiO8As5qjrkkSV1PhLAt+55a4Hem49SNdcY8dCvB5cWrfIW+SbmxD9HOr4Oht1gzu4CtbtjZ84q4Odi/yqqvcJ7q8uIpuTXdLWubtoxA7yV8UkiFFYndlcVu+HAyuJJR2UAlrKV+z6U8t8fWJ8RQxKPdCBOPpLQOXktAqge+qeQclBLGquygwdvZ1It/XK6biql9Du3yGLfIZuu0o2nazX678=
""",
    inputs = parse("68.1 Urea + 41.7 Copper Plate + 20.8 Glass + 13.9 Crushed Quartz + 438 Methane + 8.33 Sulfur + 8.33 Kevlar + 8.33 Photophore + 8.33 Iron-niobium alloy + 6.25 Silver + 250 Niobium Complex + 208 Sulfuric Acid + 4.17 Aramid Fiber + 104 Benzene + 104 Hot Air + 83.3 Organic Solvent + 8.43 MW"),
    outputs = parse("25 Optical Fiber"),
    registers = [test_report, current])


if __name__ == '__main__':
    # TODO assert that all line names are unique
    
    with open("fixme.txt", "w") as file:
        file.writelines([f"\n    Thing(\"{missing.title()}\", UNKNOWN_STACK_SIZE)," for missing in COULD_NOT_FIND])
    # print("\n\n".join())
    print()
    print(automation_science)
    print(optical_fiber)
    print()
    test_report.report()