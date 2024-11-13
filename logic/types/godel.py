def implication(x, y):
    return 1 if x<=y else y

def conjunction(x, y):
    return min(x, y)

def negation(x):
    return 1 if x<=0 else 0  # implication(x, 0)

def weak_negation(x):
    return 1-x

def text():
    return ("Reasoning is as weak as its weakest statement. "
            "\nFor example, if you believe that A has truth value 0.5 and B truth value 0.7, "
            "\nthen both of them holding true simultaneously has truth value 0.5.")