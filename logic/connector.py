import sqlite3
from logic.manager import Manager


class Connector:
    def __init__(self, database='managers.db'):
        self.database = database
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.database) as conn:
            with open('schema.sql', 'r') as f:
                conn.executescript(f.read())

    def _connect(self):
        conn = sqlite3.connect(self.database)
        conn.row_factory = sqlite3.Row
        return conn

    def __getitem__(self, name):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM managers WHERE name = ?", (name,))
            manager_row = cursor.fetchone()
            if not manager_row:
                raise KeyError(f"Manager with name '{name}' not found.")

            # Retrieve predicates and descriptions
            cursor.execute("SELECT symbol, description FROM predicates WHERE manager_id = ?", (manager_row['id'],))
            predicates = {row['symbol']: row['description'] for row in cursor.fetchall()}

            # Retrieve expressions
            cursor.execute("SELECT symbol, expression FROM expressions WHERE manager_id = ?", (manager_row['id'],))
            expressions = {row['symbol']: row['expression'] for row in cursor.fetchall()}

            # Create and populate Manager
            manager = Manager(owner=manager_row['owner'], **expressions)
            manager.predicates = predicates
            return manager

    def __setitem__(self, name, manager):
        if not isinstance(manager, Manager):
            raise ValueError("Only Manager objects can be stored.")

        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM managers WHERE name = ?", (name,))
            manager_row = cursor.fetchone()

            if manager_row:
                # Update existing manager
                manager_id = manager_row['id']
                cursor.execute("UPDATE managers SET owner = ? WHERE id = ?", (manager.owner, manager_id))
                cursor.execute("DELETE FROM predicates WHERE manager_id = ?", (manager_id,))
                cursor.execute("DELETE FROM expressions WHERE manager_id = ?", (manager_id,))
            else:
                # Insert new manager
                cursor.execute("INSERT INTO managers (name, owner) VALUES (?, ?)", (name, manager.owner))
                manager_id = cursor.lastrowid

            print(manager.predicates)

            # Insert all predicates and descriptions
            for symbol, description in manager.predicates.items():
                cursor.execute("INSERT INTO predicates (manager_id, symbol, description) VALUES (?, ?, ?)",
                               (manager_id, symbol, description))

            # Insert all expressions
            for symbol, expression in manager.expressions.items():
                cursor.execute("INSERT INTO expressions (manager_id, symbol, expression) VALUES (?, ?, ?)",
                               (manager_id, symbol, expression))

            conn.commit()

    def pop(self, name, _=None):
        assert _ is None
        self.__delitem__(name)

    def __delitem__(self, name):
        """Delete a Manager object by name."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM managers WHERE name = ?", (name,))
            manager_row = cursor.fetchone()
            if not manager_row:
                raise KeyError(f"Manager with name '{name}' not found.")

            cursor.execute("DELETE FROM managers WHERE id = ?", (manager_row['id'],))
            conn.commit()

    def __iter__(self):
        """List all manager names."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM managers")
            return [row['name'] for row in cursor.fetchall()].__iter__()

    def __contains__(self, name):
        """Check if a Manager exists by name."""
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM managers WHERE name = ?", (name,))
            return cursor.fetchone() is not None

    def get(self, name):
        try:
            return self[name]
        except KeyError:
            return None

    def items(self):
        with self._connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM managers")
            manager_names = [row['name'] for row in cursor.fetchall()]
            return ((name, self[name]) for name in manager_names)
