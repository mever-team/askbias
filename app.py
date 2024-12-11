from flask import Flask, render_template, request, redirect, url_for, session
from flask_htpasswd import HtPasswdAuth
from logic.types import product, lukasiewicz, godel
from logic.expression import Context
from logic.manager import Manager
from logic.connector import Connector
import os


def load_secret_key(file_path):
    if "FLASK_SECRET" in os.environ:
        return os.environ["FLASK_SECRET"]
    # have a file-based secret key management
    try:
        with open(file_path, 'rb') as secret_file:
            return secret_file.read().strip()
    except FileNotFoundError:
        secret_key = os.urandom(64)
        with open(file_path, 'wb') as f:
            f.write(secret_key)
        print(f"Secret key generated for the first time and saved to {file_path}.\nDO NOT SHARE THE SECRET KEY FILE")
        return secret_key
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the secret key: {e}")


def create_defaults(manager):
    manager.predicates = {  # Default descriptions
        "S": "protected group members are encountered",
        "E": "there is discrimination against the group",
        "M": "correct predictions for the group",
        "Mc": "correct predictions for other groups",
        "T": "numerical deviation could imply discrimination",
        "tol": "acceptable numerical deviation from target truth values"
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
app.config['FLASK_HTPASSWD_PATH'] = 'secrets/.htpasswd'  # htpasswd -c secrets/.htpasswd my_username (without -c for more users)
app.config['FLASK_SECRET'] = load_secret_key('secrets/flask_secret.txt')
app.config['SECRET_KEY'] = app.config['FLASK_SECRET']
htpasswd = HtPasswdAuth(app)
managers = Connector()

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = session.get('user', '')
    is_guest = len(user)==0
    if request.method == 'POST':
        if request.form.get('expert') is None:
            session['user'] = ''  # Set empty user for guest
            return redirect(url_for('index'))
        else:
            username = request.form.get('username', '')
            password = request.form.get('password', '')
            valid, username = htpasswd.check_basic_auth(username, password)
            if valid:  # Verify credentials
                session['user'] = username
                return redirect(url_for('index'))
            else:
                return render_template('login.html',
                                       user=user,
                                       is_guest=is_guest,
                                       error="The username and password combination were either not found or incorrect.")
    return render_template('login.html', user=user, is_guest=is_guest)


@app.route('/')
def index():
    user = session.get('user', '')
    is_guest = len(user)==0
    return render_template('index.html', managers=managers, user=user, is_guest=is_guest)


@app.route('/manager/new', methods=['GET', 'POST'])
def new_manager():
    user = session.get('user', '')
    is_guest = len(user)==0
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
        manager = Manager(**expressions, owner=user)
        manager.predicates = predicates
        managers[name] = manager
        return redirect(url_for('index'))
    manager = Manager(owner=user)
    create_defaults(manager)  # Populate with default predicates and expressions
    return render_template('manager_form.html', name="", manager=manager, user=user, is_guest=is_guest)



@app.route('/manager/<name>/edit', methods=['GET', 'POST'])
def edit_manager(name):
    user = session.get('user', '')
    is_guest = len(user)==0
    manager = managers.get(name)
    if not manager:
        return redirect(url_for('index'))

    if request.method == 'POST':
        if 'delete' in request.form:
            if user!="mammoth" and user!=manager.owner:
                return redirect(url_for('index'))
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
        is_updating = request.form.get("update") is not None

        if is_updating and(user == "mammoth" or user==manager.owner):
            # Remove the old manager if the name has changed
            managers.pop(name, None)

        error = ""
        if new_name in managers:
            error = "A measure with the same name has already been created. A different name was automatically assigned."
            inc = 2
            nn = "#".join(new_name.split("#")[:-1]) if "#" in new_name else new_name
            while new_name in managers:
                new_name = nn+"#"+str(inc)
                inc += 1

        # Create a new manager or update existing one, then set defaults
        manager = Manager(**expressions, owner=user)
        manager.predicates.update(predicates)
        managers[new_name] = manager

        if error:
            return render_template('manager_form.html', manager=manager, name=new_name, is_guest=is_guest, user=user, error=error)

        return redirect(url_for('index'))
    return render_template('manager_form.html', manager=manager, name=name, is_guest=is_guest, user=user)


@app.route('/manager/<name>/delete', methods=['POST'])
def delete_manager(name):
    user = session.get('user', '')
    is_guest = len(user)==0
    manager = managers.get(name)
    if not manager or (user!="mammoth" and user!=manager.owner):
        return redirect(url_for('index'))
    managers.pop(name, None)
    return redirect(url_for('index'))


@app.route('/manager/<name>/evaluate')
def manager_evaluate(name, values):
    user = session.get('user', '')
    is_guest = len(user)==0
    manager = managers.get(name)
    return render_template('manager_evaluate.html', name=name, values=values, manager=manager, user=user, is_guest=is_guest)


@app.route('/manager/<name>/inputs', methods=['GET', 'POST'])
def manager_inputs(name):
    user = session.get('user', '')
    is_guest = len(user)==0
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
        return render_template('manager_evaluate.html', name=name, values=values, manager=manager, user=user, is_guest=is_guest)

    return render_template('manager_inputs.html', name=name, manager=manager, predicates=manager.predicates, logic_types=logic_types, user=user, is_guest=is_guest)


if __name__ == '__main__':
    app.run(debug=False)
