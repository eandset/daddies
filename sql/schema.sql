-- name: create_schema#
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    vk_id INTEGER UNIQUE NOT NULL,
    first_name TEXT,
    eco_points INTEGER DEFAULT 0,
    eco_level TEXT DEFAULT 'Новичок',
    preferences TEXT DEFAULT 'all'
);

CREATE TABLE IF NOT EXISTS eco_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    lat REAL,
    lon REAL,
    category TEXT
);

-- Заполним пару тестовых точек для демо
INSERT OR IGNORE INTO eco_points (name, description, category)
VALUES
('Эко-Сбор Центр', 'Прием пластика и стекла', 'recycle'),
('Зеленый Парк', 'Место для субботников', 'event');