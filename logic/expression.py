from collections.abc import Iterable

class Context:
    def __init__(self, logic, **kwargs):
        self.values = kwargs | {"true": 1, "false": 0}
        self.logic = logic

    def insert(self, alias, expression):
        self.values[alias] = expression.evaluate(self)
        return self


class Expression:
    def __init__(self, operation, *args):
        self.args = args
        self.operation = operation

    def evaluate(self, context: Context):
        evaluated_args = [arg.evaluate(context) for arg in self.args]
        operation = getattr(context.logic, self.operation)
        result = evaluated_args[0]
        if len(evaluated_args)==1:
            result = operation(result)
        for arg in evaluated_args[1:]:
            result = operation(result, arg)
        if isinstance(result, Iterable):
            combine = 1
            for value in result:
                combine = context.logic.conjunction(combine, value)
            return combine
        return result

    def text(self, tab="", fromConjunction=False, injectNegation=False, **kwargs):
        ret = ""
        if self.operation=="conjunction":
            if not fromConjunction:
                ret += "ALLOW ALL THESE TO BE SATISFIED\n" if injectNegation else "ALL THESE ARE SATISFIED\n"
                tab += " •"
                ret += tab+self.args[0].text(tab, True, **kwargs)
            else:
                ret += self.args[0].text(tab, True, **kwargs)
            for arg in self.args[1:]:
                if ret[-1]!="\n":
                    ret += "\n"
                ret += tab+arg.text(tab, True, **kwargs)
                if ret[-1]!="\n":
                    ret += "\n"
        elif self.operation=="implication":
            ret += "ALLOW THAT GIVEN " if injectNegation else "GIVEN "
            ret += self.args[0].text(tab, **kwargs)
            if ret[-1]!="\n":
                ret += " "
            else:
                ret += tab
            ret += "THEN " if injectNegation else "THEN "
            ret += self.args[1].text(tab, **kwargs)
            if ret[-1]!="\n":
                ret += "\n"
        elif self.operation=="negation":
            ret += "DO NOT "+self.args[0].text(tab, injectNegation=True, **kwargs)
        elif self.operation=="weak_negation":
            ret += "DISAGREE THAT "+self.args[0].text(tab, **kwargs)
        else:
            raise Exception("Invalid operation"+str(self.operation))
        return ret


class Symbol:
    def __init__(self, name):
        self.name = name

    def text(self, tab="", fromConjunction=False, injectNegation=False, **kwargs):
        if injectNegation:
            return "ALLOW "+self.text(tab, fromConjunction, injectNegation=False, **kwargs)
        if self.name in kwargs and kwargs[self.name]:
            return kwargs[self.name]
        return self.name

    def evaluate(self, context: Context):
        return context.values.get(self.name)