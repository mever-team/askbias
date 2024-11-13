from lark import Lark, Transformer, v_args
from logic.expression import *

grammar = r"""
    start: implication
    ?implication: conjunction ("=>" conjunction)*
    ?conjunction: negation ("&" negation)*
    ?negation: "!" primary -> strong_negation
             | "-" primary -> weak_negation
             | primary
    ?primary: SYMBOL
            | "(" implication ")"

    SYMBOL: /[a-zA-Z_][a-zA-Z0-9_'\@\[\]\{\}]*/
    %ignore /\s+/
"""

parser = Lark(grammar, start='start')

@v_args(inline=True)
class ExpressionTransformer(Transformer):
    def implication(self, *args):
        return Expression('implication', *args)

    def conjunction(self, *args):
        return Expression('conjunction', *args)

    def strong_negation(self, expr):
        return Expression('negation', expr)

    def weak_negation(self, expr):
        return Expression('weak_negation', expr)

    def SYMBOL(self, token):
        return Symbol(str(token))

    def start(self, expr):
        return expr


def parse(expression):
    tree = parser.parse(expression)
    transformer = ExpressionTransformer()
    return transformer.transform(tree)
