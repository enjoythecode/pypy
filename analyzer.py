from collections import defaultdict
from ortools.linear_solver import pywraplp
from defs import T

class Analyzer():
    def __init__(self):
        self.lines = []
    
    def register(self, line):
        self.lines += [line]


    def analysis(self, targets, thing_dict, prevent_faucet = []):
        initial_wats, thing_flow_details = self.sub_analysis(targets, thing_dict, prevent_faucet, verbose = False)
        assert initial_wats is not None
        initial_wats = set(initial_wats)

        kowalski_insights = {}

        with open("report.txt", "w") as file:
            file.writelines(thing_flow_details.values())

        for wat in initial_wats:
            after_wat, _ = self.sub_analysis(targets, thing_dict, prevent_faucet + [wat], verbose = False)
            if after_wat is None:
                kowalski_insights[wat] = f"restricting {wat} was infeasible"
                continue
            kowalski_insights[wat] = f"restricting {wat} added a need for {set(after_wat) - initial_wats}"

        for key, val in kowalski_insights.items():
            print(val)
            print(thing_flow_details[key])

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
            
            new_f = solver.NumVar(0, ub if thing_dict[thing].should_faucet else 0, f"faucet::{thing}")
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
