def implication(x, y):
    return 1 if x<=y else y/x

def conjunction(x, y):
    return x*y

def negation(x):
    return 1 if x==0 else 0  # implication(x, 0)

def weak_negation(x):
    return 1-x

def text():
    return ("Reasoning with statements not fully wrong is never fully wrong."
            "\nThis is a generalization of probability theory; non-zero probabilities do not "
            "\nvanish, regardless of how small they become. "
            "\nFor example, if you believe that A has truth value 0.5 and B truth value 0.5, "
            "\nthen both of them holding true simultaneously has truth value 0.35.")