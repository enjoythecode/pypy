from collections import defaultdict
from ortools.linear_solver import pywraplp
from defs import T
import copy

class Analyzer():
    def __init__(self):
        self.lines = []
    
    def register(self, line):
        self.lines += [line]


    def analysis(self, targets, thing_dict, prevent_faucet = []):
        defs_prevent_faucet = []
        meta_prevent_faucet = []
        for thing in thing_dict:
            if not thing_dict[thing].should_faucet:
                defs_prevent_faucet += [thing]
            if "META_" in thing.upper() or "SCIENCE PACK" in thing.upper() or "VATBRAIN CARTRIDGE" in thing.upper() or "__SYN" in thing.upper():
                meta_prevent_faucet += [thing]

        all_prevents = copy.deepcopy(defs_prevent_faucet) + copy.deepcopy(meta_prevent_faucet) + copy.deepcopy(prevent_faucet)

        initial_prevents = copy.deepcopy(all_prevents)
        initial_wats, thing_flow_details = self.sub_analysis(targets, thing_dict, initial_prevents, verbose = False)
        if initial_wats is None:
            print("OOOOPS, no solution could be found. i am relaxing restrictions from defs.py except those with META_ in it, also the temp forced restrictions")
            initial_prevents = initial_prevents - defs_prevent_faucet
            initial_wats, thing_flow_details = self.sub_analysis(targets, thing_dict, initial_prevents, verbose = False)

        if initial_wats is None:
            print("ZOUCHERS! no solution could be found. i am relaxing restrictions from defs.py except those with META_ in it, AND THAT'S IT")
            initial_prevents = initial_prevents - prevent_faucet
            initial_wats, thing_flow_details = self.sub_analysis(targets, thing_dict, initial_prevents, verbose = False)


        initial_wats_set = set(initial_wats)
        initial_wats = sorted(list(initial_wats_set))
        # TODO missing some output for members of initial_wats
        kowalski_insights = {}

        with open("report.txt", "w") as file:
            file.writelines(thing_flow_details.values())

        for wat in initial_wats:
            seen = set()
            i = 0
            stack = copy.deepcopy([wat])
            while stack:
                curr = stack.pop()
                if curr in seen:
                    continue
                seen.add(curr)
                (after_wat, after_thing_flow_details) = self.sub_analysis(targets, thing_dict, initial_prevents + list(seen), verbose = False)
                if after_wat is None:
                    kowalski_insights[curr] = f"[#{i}] restricting {curr} was infeasible\n" 
                    continue
                added_need = set(after_wat) - initial_wats_set
                kowalski_insights[curr] = f"[#{i}] restricting {curr} added a need for {added_need}\n" + after_thing_flow_details[curr]
                print(">>", added_need)
                stack.extend(added_need)
                print("!!", len(stack))
                i += 1

        for key, val in kowalski_insights.items():
            print(key, val)
            # print(thing_flow_details[key])

        print(len(kowalski_insights))


    def sub_analysis(self, targets, thing_dict, prevent_faucet_on = [], verbose = False):

        print("Kowalski, analysis!")

        solver = pywraplp.Solver.CreateSolver("GLOP")
        assert solver, "could not create solver"

        # gather all lines
        line_coeffs = {}
        non_sink_or_zi_line_coeffs = []
        for line in self.lines:
            line_coeffs[line.name] = solver.NumVar(0, 1, line.name)
            if len(line.inputs) + len(line.outputs) == 1:
                non_sink_or_zi_line_coeffs.append(line_coeffs[line.name])

        # gather all the things and make 
        thing_inputs = defaultdict(list)
        for line in self.lines:
            for irate in line.inputs.values():
                thing_inputs[irate.thing.name].append(line)
        
        thing_outputs = defaultdict(list)
        for line in self.lines:
            for orate in line.outputs.values():
                thing_outputs[orate.thing.name].append(line)

        things = set()
        for k in thing_inputs:
            things.add(k)
        for k in thing_outputs:
            things.add(k)
        for k in targets:
            things.add(k.thing.name)

        things = sorted(things)
        
        faucet_indices  = {}
        faucets         = []
        faucet_index_to_thing = {}
        for i, thing in enumerate(things):
            assert thing in thing_dict, f"could not find {thing} in thing_dict"
            ub = solver.infinity()
            if thing in prevent_faucet_on:
                if verbose:
                    print("*** ignoring ", thing, " because it is in ", prevent_faucet_on)
                ub = 0
            
            new_f = solver.NumVar(0, ub, f"faucet::{thing}")
            faucet_indices[thing] = i
            faucet_index_to_thing[i] = thing
            faucets.append(new_f)

        total_production_per_thing = {}
        # generate constraints for the things
        for thing in things:
            total_production_for_thing = sum([line_coeffs[line.name] * line.net_flow_for_thing(thing) for line in thing_inputs[thing]])
            total_production_per_thing[thing] = total_production_for_thing    
            solver.Add( 0 == (
                -sum([tgt.amount if tgt.thing.name == thing else 0 for tgt in targets]) +
                faucets[faucet_indices[thing]] +
                # sum([line_coeffs[line.name] * line.net_flow_for_thing(thing) for line in thing_inputs[thing]]) +
                total_production_for_thing +
                sum([line_coeffs[line.name] * line.net_flow_for_thing(thing) for line in thing_outputs[thing]]))
            )

        solver.Minimize(sum(faucets))# - sum(non_sink_or_zi_line_coeffs) / 100)
        res = solver.Solve()
        if res == solver.INFEASIBLE:
            return None, []


        if (verbose):
            print(" === UTILIZATION ===")
            for key, val in line_coeffs.items():
                if val.solution_value() > 0:
                    print(f"line::{key} = {val.solution_value()}")
            print()

        needed_help = []

        if verbose:
            print(" === NEEDS MORE PRODUCTION ===")
        
        for thing in things:
            if faucets[faucet_indices[thing]].solution_value() > 0:
                needed_help.append(thing)
                if verbose:
                    print(f"faucet::{thing} = {faucets[faucet_indices[thing]].solution_value()}")
        if verbose:
            print()
        

        thing_flow_details = {}
        for thing in things:
            out = []
            # if 'SYNG' not in thing:
            #     continue

            faucet_amount = faucets[faucet_indices[thing]].solution_value()

            faucet_prod = faucets[faucet_indices[thing]].solution_value()
            total_consumption = sum([line_coeffs[line.name].solution_value() * line.net_flow_for_thing(thing) for line in thing_inputs[thing]])
            total_production = sum([line_coeffs[line.name].solution_value() * line.net_flow_for_thing(thing) for line in thing_outputs[thing]])
            

            # if (total_production + faucet_prod) < 0.01:
            #     continue
            out.append("\n\n")
            out.append(" ==== " + thing)

            # print(faucet_prod)
            # print(total_consumption)
            # print(total_production)

            out.append("")

            out.append(f" + {faucets[faucet_indices[thing]].solution_value()} from FAUCET")
            
            for line in thing_outputs[thing]:
                out.append(f" + {line_coeffs[line.name].solution_value() * line.net_flow_for_thing(thing)} with {round(line_coeffs[line.name].solution_value() * 100, 2)}% of {line.name}")

            out.append("")

            for line in thing_inputs[thing]:
                out.append(f" - {line_coeffs[line.name].solution_value() * -line.net_flow_for_thing(thing)} with {round(line_coeffs[line.name].solution_value() * 100, 2)}% of {line.name}")
            

            out.append("")
            thing_flow_details[thing] = "\n".join(out)


        return (needed_help, thing_flow_details)
