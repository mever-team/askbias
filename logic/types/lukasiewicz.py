def implication(x, y):
    return min(1, 1-x+y)

def conjunction(x, y):
    return max(x+y-1, 0)

def negation(x):
    return 1-x  # implication(x, 0)

def weak_negation(x):
    return 1-x

def text():
    return ("Reasoning with partially true statements eventually becomes fully wrong. "
            "\nFor example, if you believe that A has truth value 0.5, B truth value 0.5, and so on, "
            "\nthen after a number of such statements you would get truth value of 0." 
            "\nThis is the only logic where NOT and DISAGREE have the same meaning.")