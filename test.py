from ortools.linear_solver import pywraplp

from helpers import parse
from classes import *
from defs import *

test_report = Analyzer()
current = Analyzer()


## objective: hit the desired production goals
## variables: how much to use each build
## constraints: inputs and outputs must match in some way

def recipes101():

    solver = pywraplp.Solver.CreateSolver("GLOP")
    assert solver, "could not create solver"

    r1 = solver.NumVar(0, 1, "r1") # 100 iron plate -> 200 iron stick
    r2 = solver.NumVar(0, 1, "r2") # 150 iron stick -> 15 auto science

    print("Number of variables =", solver.NumVariables())

    solver.Add(r1 * 200 == r2 * 150) # iron stick must balance

    print("Number of constraints =", solver.NumConstraints())

    solver.Maximize(r2) # get me as many auto science as possible

    print(f"Solving with {solver.SolverVersion()}")
    solver.Solve()

    print("Solution:")
    print("x =", r1.solution_value())
    print("y =", r2.solution_value())

def recipes_cant_make_enough():

    solver = pywraplp.Solver.CreateSolver("GLOP")
    assert solver, "could not create solver"

    
    r1 = solver.NumVar(0, 1, "r1") # 100 iron plate -> 200 iron stick
    r2 = solver.NumVar(0, 1, "r2") # 150 iron stick -> 15 auto science
    
    faucet1 = solver.NumVar(0, solver.infinity(), "faucet_r1")
    faucet2 = solver.NumVar(0, solver.infinity(), "faucet_r2")

    print("Number of variables =", solver.NumVariables())

    solver.Add(faucet1 + r1 * 200 == r2 * 150) # iron stick must balance
    solver.Add(faucet2 + r2 * 15 >= 20) # get me at least 20 auto science

    print("Number of constraints =", solver.NumConstraints())

    solver.Minimize(faucet1 + faucet2) # get me as many auto science as possible

    print(f"Solving with {solver.SolverVersion()}")

    res = solver.Solve()
    assert res != solver.INFEASIBLE

    print(res == solver.INFEASIBLE)

    print("Solution:")
    print("x =", r1.solution_value())
    print("y =", r2.solution_value())
    print("f1 =", faucet1.solution_value())
    print("f2 =", faucet2.solution_value())

def using_python_list_comp():

    solver = pywraplp.Solver.CreateSolver("GLOP")
    assert solver, "could not create solver"

    
    r1 = solver.NumVar(0, 1, "r1") # 100 iron plate -> 200 iron stick
    r2 = solver.NumVar(0, 1, "r2") # 150 iron stick -> 15 auto science
    
    faucet1 = solver.NumVar(0, solver.infinity(), "faucet_r1")
    faucet2 = solver.NumVar(0, solver.infinity(), "faucet_r2")

    print("Number of variables =", solver.NumVariables())

    recipe1rates = {
        "t0": -100,
        "t1": 200
    }
    recipe2rates = {
        "t1": -150,
        "t2": 14
    }

    recipes = {
        "r1": recipe1rates,
        "r2": recipe2rates
    }
    
    rate_coeffs = {
        "r1": r1,
        "r2": r2
    }

    t1_affectors = ["r1", "r2"]
    t2_affectors = ["r2"]
     
    # assert sum([recipe[thing_id] for recipe in t1_affectors]) == 50
        
    thing_id = "t1"
    solver.Add(faucet1 + sum([rate_coeffs[recipe] * recipes[recipe][thing_id] for recipe in t1_affectors]) == 0) # iron stick must balance
    thing_id = "t2"
    solver.Add(faucet2 + r2 * recipe2rates["t2"] >= 20) # get me at least 20 auto science

    # solver.Add(faucet2 + r2 * 15 >= 20) # get me at least 20 auto science

    print("Number of constraints =", solver.NumConstraints())

    solver.Minimize(faucet1 + faucet2) # get me as many auto science as possible

    print(f"Solving with {solver.SolverVersion()}")

    res = solver.Solve()
    assert res != solver.INFEASIBLE

    print(res == solver.INFEASIBLE)

    print("Solution:")
    print("x =", r1.solution_value())
    print("y =", r2.solution_value())
    print("f1 =", faucet1.solution_value())
    print("f2 =", faucet2.solution_value())

def kowalski101():
    kowalski = Analyzer()

    r0 = Line("ZI Log", "", inputs=parse(""),
    outputs = parse("10000 LoG"),
    registers = [kowalski])

    r1 = Line("LogToAsh", "",
    inputs = parse("150 Log"),
    outputs = parse("100 Ash"),
    registers = [kowalski])

    r2 = Line("AshToSilver", "",
    inputs = parse("150 Ash"),
    outputs = parse("15 Silver"),
    registers = [kowalski])

    kowalski.analysis(parse("20 Silver"))

if __name__ == '__main__':
    recipes101()
    recipes_cant_make_enough()
    using_python_list_comp()
    kowalski101()