from flask import Flask, render_template, request, redirect, url_for
from logic.types import product, lukasiewicz, godel
from logic.expression import Context
from logic.manager import Manager


def create_defaults(manager):
    manager.predicates = {  # Default descriptions
        "S": "protected group members are encountered",
        "E": "there is discrimination against the group",
        "M": "correct predictions for the group",
        "Mc": "correct predictions for other groups",
        "T": "numerical tolerance is small",
        "tol": "large numerical deviation from target truth values"
    }
    manager.expressions = {  # Default formulas
        "M": "",
        "Mc": "",
        "tol": "",
        "S": "",
        "E": "-((M=>Mc)&(Mc=>M))",
        "T": "!(-(tol=>{E}))",
        "bias": "S&{E}&{T}",
        "fairness": "!{bias}"
    }


app = Flask(__name__)
managers = {}

@app.route('/')
def index():
    return render_template('index.html', managers=managers)


@app.route('/manager/new', methods=['GET', 'POST'])
def new_manager():
    if request.method == 'POST':
        name = request.form['name']
        expressions = dict()
        predicates = dict()
        for key in request.form.keys():
            if key.startswith('symbol_'):
                index = key.split('_')[1]
                symbol = request.form[f'symbol_{index}']
                expressions[symbol] = request.form.get(f'expression_{index}', '')
                predicates[symbol] =  request.form.get(f'description_{index}', '')
        managers[name] = Manager(**expressions)
        managers[name].predicates = predicates
        return redirect(url_for('index'))
    manager = Manager()
    create_defaults(manager)  # Populate with default predicates and expressions
    return render_template('manager_form.html', name="", manager=manager)



@app.route('/manager/<name>/edit', methods=['GET', 'POST'])
def edit_manager(name):
    manager = managers.get(name)
    if not manager:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'delete' in request.form:
            # Delete the manager
            managers.pop(name, None)
            return redirect(url_for('index'))

        # Collect the form data for expressions and predicates
        expressions = {}
        predicates = {}
        for key in request.form.keys():
            if key.startswith('symbol_'):
                index = key.split('_')[1]
                symbol = request.form[f'symbol_{index}']
                expression = request.form.get(f'expression_{index}', '')
                description = request.form.get(f'description_{index}', '')

                expressions[symbol] = expression
                predicates[symbol] = description

        # Check for a name change and handle accordingly
        new_name = request.form.get('name')
        if new_name != name:
            # Remove the old manager if the name has changed
            managers.pop(name, None)

        # Create a new manager or update existing one, then set defaults
        manager = Manager(**expressions)
        manager.predicates.update(predicates)
        managers[new_name] = manager

        return redirect(url_for('index'))
    return render_template('manager_form.html', manager=manager, name=name)


@app.route('/manager/<name>/delete', methods=['POST'])
def delete_manager(name):
    managers.pop(name, None)
    return redirect(url_for('index'))


@app.route('/manager/<name>/evaluate')
def manager_evaluate(name, values):
    manager = managers.get(name)
    return render_template('manager_evaluate.html', name=name, values=values, manager=manager)


@app.route('/manager/<name>/inputs', methods=['GET', 'POST'])
def manager_inputs(name):
    manager = managers.get(name)
    if not manager:
        return redirect(url_for('index'))  # Redirect if manager does not exist

    # Example logic types and descriptions
    logic_types = {
        'Product logic': product.text(),
        'Lukasiewicz logic': lukasiewicz.text(),
        'Godel logic': godel.text(),
    }

    if request.method == 'POST':
        selected_logic = request.form.get('logic_type')
        context_data = {key: float(value) for key, value in request.form.items() if value and key != 'logic_type'}
        selected_logic = selected_logic.lower()# if selected_logic is not None else "product logic"
        if selected_logic == 'godel logic':
            selected_logic = godel
        elif selected_logic == 'product logic':
            selected_logic = product
        else:
            selected_logic = lukasiewicz
        context = Context(selected_logic, **context_data)  # Use selected logic type
        manager.evaluate(context)
        values = [(manager.predicates.get(k, k) if manager.predicates.get(k, k) else k,
                   (k+" = " if manager.expressions.get(k, "") else k)+manager.expressions.get(k, "").replace("{", "").replace("}", ""),
                   v, k) for k, v in context.values.items()]
        return render_template('manager_evaluate.html', name=name, values=values, manager=manager)

    return render_template('manager_inputs.html', name=name, manager=manager, predicates=manager.predicates, logic_types=logic_types)


if __name__ == '__main__':
    app.run(debug=False)
