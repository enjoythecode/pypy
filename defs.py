from classes import *

UNKNOWN_STACK_SIZE = -1

__ = [
    Thing("Native Flora", 50),
    Thing("Log", 100),
    Thing("Ash", 1000),
    Thing("Stone Brick", 100),
    Thing("Iron Plate", 100),
    Thing("Copper Plate", 100),
    Thing("Automation Science Pack", 200),
    Thing("MW", 1),

    Thing("Urea", 100),
    Thing("Glass", 100),
    Thing("Crushed Quartz", UNKNOWN_STACK_SIZE),
    Thing("Methane", UNKNOWN_STACK_SIZE),
    Thing("Sulfur", UNKNOWN_STACK_SIZE),
    Thing("Kevlar", UNKNOWN_STACK_SIZE),
    Thing("Photophore", UNKNOWN_STACK_SIZE),
    Thing("Iron-Niobium Alloy", UNKNOWN_STACK_SIZE),
    Thing("Silver", UNKNOWN_STACK_SIZE),
    Thing("Niobium Complex", UNKNOWN_STACK_SIZE),
    Thing("Sulfuric Acid", UNKNOWN_STACK_SIZE),
    Thing("Aramid Fiber", UNKNOWN_STACK_SIZE),
    Thing("Benzene", UNKNOWN_STACK_SIZE),
    Thing("Hot Air", UNKNOWN_STACK_SIZE),
    Thing("Organic Solvent", UNKNOWN_STACK_SIZE),
    Thing("Optical Fiber", UNKNOWN_STACK_SIZE),
]

T = {}

for _ in __:
    # if _.stack_size == UNKNOWN_STACK_SIZE:
    #     assert False, _.name

    T[_.name.upper()] = _
