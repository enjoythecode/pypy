from collections import defaultdict
from ortools.linear_solver import pywraplp


class Thing():
    def __init__(self, name, stack_size):
        self.name = name
        self.stack_size = stack_size

class Analyzer():
    def __init__(self):
        self.lines = []
    
    def register(self, line):
        self.lines += [line]

    def analysis(self, targets):
        print("Kowalski, analysis!")

        solver = pywraplp.Solver.CreateSolver("GLOP")
        assert solver, "could not create solver"

        # gather all lines
        line_coeffs = {}
        for line in self.lines:
            line_coeffs[line.name] = solver.NumVar(0, 1, line.name)

        # gather all the things and make 
        thing_inputs = defaultdict(list)
        for line in self.lines:
            for irate in line.inputs:
                thing_inputs[irate.thing.name].append(line)
        
        thing_outputs = defaultdict(list)
        for line in self.lines:
            for orate in line.outputs:
                thing_outputs[orate.thing.name].append(line)

        things = set()
        for k in thing_inputs:
            things.add(k)
        for k in thing_outputs:
            things.add(k)
        
        faucet_indices  = {}
        faucets         = []
        for i, thing in enumerate(things):
            new_f = solver.NumVar(0, solver.infinity(), f"faucet::{thing}")
            faucet_indices[thing] = i
            faucets.append(new_f)

        # generate constraints for the things
        for thing in things:
            solver.Add( 0 == (
                -sum([tgt.amount if tgt.thing.name == thing else 0 for tgt in targets]) +
                faucets[faucet_indices[thing]] +
                sum([line_coeffs[line.name] * line.net_flow_for_thing(thing) for line in thing_inputs[thing]]) +
                sum([line_coeffs[line.name] * line.net_flow_for_thing(thing) for line in thing_outputs[thing]]))
            )

        solver.Minimize(sum(faucets))
        res = solver.Solve()
        assert res != solver.INFEASIBLE, "infeasible!"

        print("not infeasible?", res != solver.INFEASIBLE)
        for thing in things:
            print(f"faucet::{thing} = {faucets[faucet_indices[thing]].solution_value()}")
        
        for key, val in line_coeffs.items():
            print(f"line::{key} = {val.solution_value()}")

        # print("Solution:")
        # print("x =", r1.solution_value())
        # print("y =", r2.solution_value())
        # print("f1 =", faucet1.solution_value())
        # print("f2 =", faucet2.solution_value())
        



class Rate():
    def __init__(self, thing, amount, priority = 0, voided = False):
        self.thing = thing
        self.amount = amount
        self.priority = priority
        self.voided = voided

    def __str__(self):
        result = str(self.amount) + " " + self.thing.name
        if self.priority != 0:
            result += f" @ {self.priority}"
        if self.voided:
            result = "(" + result + ")"
        return result

class Line():
    def __init__(self, name, string, inputs, outputs, registers):
        self.name = name
        self.string = string
        self.inputs = inputs
        self.outputs = outputs
        for reg in registers:
            reg.register(self)
        
    def net_flow_for_thing(self, name):
        net_flow = 0
        for r in self.inputs:
            if r.thing.name == name:
                net_flow -= r.amount
        for r in self.outputs:
            if r.thing.name == name:
                net_flow += r.amount

        return net_flow

    def __str__(self):
        result = f"### {self.name}\n"
        result += " + ".join([str(o) for o in self.outputs]) + "\n"
        result += "> " + " + ".join([str(i) for i in self.inputs]) + "\n"
        return result

