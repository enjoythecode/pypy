from defs import *

MINING_PROD = 1.1

COULD_NOT_FIND = set()

def parse(s):

    parts = s.split("+")
    result = []
    for part in parts:
        if len(part) == 0:
            continue
            
        stripped = part.strip(" ")


        voidable = stripped[0] == "("
        affected_by_mining_prod = part[0] == "{"

        stripped = stripped.strip("() {}")

        first_space = stripped.find(" ")
        assert first_space > -1, f"could not find space in {stripped}"

        number_part = stripped[:first_space]
        
        has_k = "k" == number_part[-1]
        if has_k:
            number_part = number_part[:-1]
        number = float(number_part) * (1000 if has_k else 1) * (MINING_PROD if affected_by_mining_prod else 1)
        text = stripped[first_space+1:].strip(" ")

        prio = 0
        if text.find("@") > -1:
            prio = int(text.split("@")[1].strip(" "))
            text = text.split("@")[0].strip(" ")

        if text.upper() not in T:
            print("could not find in T: ", text.upper())
            COULD_NOT_FIND.add(text.upper())
        else:
            result.append(Rate(T[text.upper()], number, prio, voidable))
        
    with open("fixme.txt", "w") as file:
        file.writelines([f"\n    Thing(\"{missing.title()}\", UNKNOWN_STACK_SIZE)," for missing in COULD_NOT_FIND])

    return result