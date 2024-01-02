from classes import *
from defs import *
from helpers import parse
from analyzer import Analyzer
from reader import parse_stations
from copy import deepcopy
import sys

def process_and_register_lines(analyzers, lines, thing_dict):
    for line in lines:
        line_outputs_copy = deepcopy(line.outputs)
        for key, inr in line_outputs_copy.items():
            # print(key, inr.voidable)
            if inr.voidable:
                uniq_key = f"__syn_{line.name}::{inr.thing.name}".upper()
                # FUTURE this is hacky way to do a deep copy...
                syn_thing = Thing(uniq_key, UNKNOWN_STACK_SIZE, should_faucet=False)
                syn_line_voiding = Line(f"{uniq_key}::VOIDING", inputs = [Rate(syn_thing, inr.amount, priority = inr.priority, voidable = False)], outputs=[])
                syn_line_conversion = Line(f"{uniq_key}::CONVERSION", inputs = [Rate(syn_thing, inr.amount, priority = inr.priority, voidable = False)], outputs=[Rate(thing_dict[inr.thing.name], inr.amount, priority=inr.priority, voidable=False)])
                for anal in analyzers:
                    anal.register(syn_line_conversion)
                    anal.register(syn_line_voiding)
                thing_dict[uniq_key.upper()] = syn_thing

                line.outputs[uniq_key] = Rate(syn_thing, inr.amount, priority = inr.priority, voidable = False)
                del line.outputs[key]

        for anal in analyzers:
            anal.register(line)

if __name__ == '__main__':
    # TODO assert that all line names are unique
    

    pypy = parse_stations("C:/Users/Sinan/S/Zettelkasten/pypy.md")

    thing_dict = T

    read_kowalski = Analyzer()
    read_kowalski_planned = Analyzer()
    process_and_register_lines([read_kowalski, read_kowalski_planned], pypy, thing_dict)

    has_extras = len(sys.argv) > 1
    num_extras = len(sys.argv[1:])
    if has_extras:
        extra_files = sys.argv[1:]
        for f in extra_files:
            print(f" >>> PROCESSING: {f} <<< ")
            additional = parse_stations("C:/Users/Sinan/S/Zettelkasten/" + f) 
            process_and_register_lines([read_kowalski_planned], additional, thing_dict)

    print()

    temp_no_faucet = ""
    temp_no_faucet += ",SELF-ASSEMBLY MONOLAYER MATERIAL,RAYON"  # why no rayon?
    # temp_no_faucet = "Nichrome,Cobalt Extract,,RAYON,SODIUM CARBONATE,LIGHTLY P-DOPED SILICON"
    # temp_no_faucet+= ",Kevlar,PLUTONIUM-238,Nylon"
    # temp_no_faucet+= ",HEAVILY N-DOPED SILICON,RARE-EARTH OXIDES,Osptical Fiber"

    
    read_kowalski.analysis(parse("1 META_TARGET_SCIENCE + 1 Meta_Target_Mall"), thing_dict,
                           prevent_faucet = [thing.upper() for thing in temp_no_faucet.split(",")])
    

    if  has_extras:
        print("\n"*10)
        print("=========\n"*10)

        
    read_kowalski_planned.analysis(parse(f"1 META_TARGET_SCIENCE + 1 Meta_Target_Mall + {num_extras} Meta_Target_Planned"), thing_dict,
                           prevent_faucet = [thing.upper() for thing in temp_no_faucet.split(",")])