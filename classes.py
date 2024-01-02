
class Thing():
    def __init__(self, name, stack_size, should_faucet = True):
        assert name[0] != " "
        assert name[-1] != " "
        self.name = name.upper()
        self.stack_size = stack_size
        self.should_faucet = should_faucet


class Rate():
    def __init__(self, thing, amount, priority = 0, voidable = False):
        self.thing = thing
        self.amount = amount
        self.priority = priority
        self.voidable = voidable

    def __str__(self):
        result = f"{self.amount} {self.thing.name}"
        if self.priority != 0:
            result += f" @ {self.priority}"
        if self.voidable:
            result = "(" + result + ")"
        return result

class Line():
    def __init__(self, name, inputs, outputs, registers = []):
        self.name = name
        self.inputs = {rate.thing.name: rate for rate in inputs}
        self.outputs = {rate.thing.name: rate for rate in outputs}
        for reg in registers:
            reg.register(self)

    def get_output(self, pin):
        for hay in self.outputs:
            if hay.thing.name == pin:
                return hay

    def get_input(self, pin):
        for hay in self.inputs:
            if hay.thing.name == pin:
                return hay
        
    def net_flow_for_thing(self, name):
        net_flow = 0
        net_flow -= self.inputs.get(name, Rate(0,0)).amount
        net_flow += self.outputs.get(name, Rate(0,0)).amount

        return net_flow

    def __str__(self):
        result = f"### {self.name}\n"
        result += " + ".join([str(o) for o in self.outputs.values()]) + "\n"
        result += "> " + " + ".join([str(i) for i in self.inputs.values()]) + "\n"
        return result

