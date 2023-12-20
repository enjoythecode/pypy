from defs import *

def parse(str):
    parts = str.split("+")
    result = []
    for part in parts:
        if len(part) == 0:
            continue
            
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