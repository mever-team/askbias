from logic.expression import Context
from logic.grammar import parse


class Manager:
    def __init__(self, **kwargs):
        self.expressions = kwargs
        self.output = list(self.expressions.keys())[-1] if kwargs else None
        self.predicates = dict()

    def expand(self):
        expressions = {k: v for k, v in self.expressions.items()}
        for k, v in expressions.items():
            k = "{"+k+"}"
            for k2, v2 in expressions.items():
                if not v2:
                    continue
                if k in v2 and k2 not in expressions:
                    expressions[k2] = v2.replace(k, "("+v+")")
        return Manager(**{self.output: expressions[self.output]})

    def text(self, **kwargs):
        ret = ""
        for k, v in self.expressions.items():
            if not v:
                continue
            if kwargs.get(k, k):
                k = kwargs.get(k, k)
            ret += "\n"+k+"\n"+"-"*len(k)+"\n"
            ret += parse(v.replace("{", "").replace("}", "")).text(**kwargs)
        return ret

    def html(self, **kwargs):
        ret = ""
        for k, v in self.expressions.items():
            if not v:
                continue
            if kwargs.get(k, k):
                k = kwargs.get(k, k)
            ret += "<h5>"+k+"</h5>"
            ret += "<pre>"+parse(v.replace("{", "").replace("}", "")).text(**kwargs)+"</pre>"
        for k, v in self.expressions.items():
            k = kwargs.get(k, k)
            if k is None or not k or len(k)==0:
                continue
            if v:
                pass
                #ret = ret.replace(k, f'<span class="px-2 border border-warning text-warning rounded bg-light" data-bs-toggle="tooltip" title="The truth value of this is automatically computed based on its definition, the selected logic, and your other beliefs.">{k}</span>')
            else:
                ret = ret.replace(k, f'''<span class="text-primary" data-bs-toggle="tooltip" title="Set  a numerical truth value or a method to compute it based on your beliefs.">{k}</span>''')
        return ret


    def html_details(self, values, **kwargs):
        if isinstance(values, list):
            values = {element[-1]: element[-2] for element in values}
        elif isinstance(values, Context):
            values = values.values
        ret = ""
        for k, v in self.expressions.items():
            prev_k = k
            if k in values:
                if values[k] == 0:
                    ret += '<i class ="bi bi-x-circle" style="color:red;"></i> '
                elif values[k] == 1:
                    ret += '<i class="bi bi-check-circle" style="color:green;"></i> '
                else:
                    ret += '<i class="bi bi-question-circle" style="color:orange;"></i> '
            if kwargs.get(k, k):
                k = kwargs.get(k, k)
            ret += "<strong>"
            ret += k
            ret += "</strong>"
            #if prev_k in values:
            #    ret += f"<span style='float:right;'>truth value {values[prev_k]:.3f}</span>"
            if not v:
                ret += "<br>"
                continue
            ret += "<pre>"+parse(v.replace("{", "").replace("}", "")).text(**kwargs)+"</pre>"
        return ret

    def html_expressions(self, **kwargs):
        ret = ""
        for k, v in self.expressions.items():
            if not v:
                continue
            original_k = k
            if kwargs.get(k, k):
                k = kwargs.get(k, k)
            ret += "<h5>"+k+"</h5>"
            ret += original_k+" = "+v.replace("{", "").replace("}", "")+"<br><br>"
        return ret

    def evaluate(self, context):
        for k, v in self.expressions.items():
            if not v:
                continue
            context.insert(k, parse(v.replace("{", "").replace("}", "")))
        return context.values[self.output]
