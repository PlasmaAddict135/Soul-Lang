
class State:
    # vals = {}
    def __init__(self):
        self.vals = dict()
    def bind(self, name, val):
        self.vals[name] = val
    def lookup(self, name):
        try:
            return self.vals[name]
        except:
            return eval(name)
    def unbind(self, name):
        return self.vals.pop(name)

class EarlyReturn(Exception):
    def __init__(self, value):
        self.value = value

class EarlyBreak(Exception):
    def __init__(self, value):
        self.value = value

class TypeReturnNode(Exception):
    pass
