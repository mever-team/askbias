from logic.types import product as logic
from logic.expression import Context
from logic.manager import Manager



manager = Manager(
    E="-((M=>Mc)&(Mc=>M))",
    T="!(-(tol=>{E}))",
    bias="S&{E}&{T}",
    fairness="!{bias}",
)

context = Context(logic,
                  S=0.2,
                  M=0.8,
                  Mc=0.78,
                  tol=0.01)

predicates = {
    "S": "protected group members are encountered",
    "E": "there is discrimination against the group",
    "M": "accurate group predictions",
    "Mc": "accurate other predictions",
    "T": "numerical tolerance is reached",
    "tol": "acceptable numerical tolerance"
}

print("Chosen logic: "+logic.text())
print(manager.text(**predicates))

manager.evaluate(context)

print("\n\n")
print("truth values")
print("------------")
for k, v in context.values.items():
    print(predicates.get(k,k).ljust(50)+f"{v:.3f}")