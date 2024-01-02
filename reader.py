from helpers import parse
from collections import defaultdict
from analyzer import Analyzer
from classes import Line

VERBOSE = True

def parse_stations(filename):

    result = []
    
    primary_name = "UNDEFINED_PRIMARY_NAME"
    secondary_count = 0

    line_outputs = None
    line_inputs = None

    with open(filename, "r") as file:
        for linen in file.readlines():
            line = linen[:-1]
            if VERBOSE:
                print(f"|||{line}" if VERBOSE else "")
            if not len(line):
                continue
            
            marker = line[0]
            if marker == "-":
                if VERBOSE:
                    print("... found stop marker, bailing" if VERBOSE else "")
                break

            if marker == "#":
                stripped = line.strip("# []")
                primary_name = stripped
                secondary_count = 0
                assert line_inputs is None, "would forget an input!"
                assert line_outputs is None, "would forget an output!"
                if VERBOSE:
                    print(f"... found #, set primary name to {stripped} and secondary count to {secondary_count}" if VERBOSE else "")

            if marker == "<":
                outputs_str = line.strip("< ")
                assert line_outputs is None, "i would be overwriting outputs!"
                line_outputs = parse(outputs_str)
                if VERBOSE:
                    print(f"... found <, parsed line outputs as {[str(x) for x in line_outputs]}" if VERBOSE else "")
                
            if marker == ">":
                inputs_str = line.strip("> ")
                assert line_inputs is None, "i would be overwriting inputs!"
                line_inputs = parse(inputs_str)
                if VERBOSE:
                    print(f"... found >, parsed line inputs as {[str(x) for x in line_inputs]}" if VERBOSE else "")
                
            if line_inputs is not None and line_outputs is not None:
                if VERBOSE:
                    print("!! constructing line because I have all the information" if VERBOSE else "")
                line_name = f"{primary_name}__subline_{secondary_count}"
                result.append(Line(line_name, inputs = line_inputs, outputs = line_outputs))
                
                line_inputs = None
                line_outputs = None
                secondary_count += 1

    return result