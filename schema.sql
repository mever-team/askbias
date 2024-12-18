CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(256) NOT NULL UNIQUE,
    owner VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS predicates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER NOT NULL,
    symbol VARCHAR(256) NOT NULL,
    description VARCHAR(256),
    FOREIGN KEY (manager_id) REFERENCES managers (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS expressions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_id INTEGER NOT NULL,
    symbol VARCHAR(256) NOT NULL,
    expression VARCHAR(256),
    FOREIGN KEY (manager_id) REFERENCES managers (id) ON DELETE CASCADE
);
