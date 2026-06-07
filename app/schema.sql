CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS rotas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    cep_origem TEXT NOT NULL,
    numero_origem TEXT NOT NULL,
    endereco_origem TEXT NOT NULL,
    origem_lat REAL,
    origem_lng REAL,
    cep_destino TEXT NOT NULL,
    numero_destino TEXT NOT NULL,
    endereco_destino TEXT NOT NULL,
    destino_lat REAL,
    destino_lng REAL,
    distancia_km REAL,
    duracao_min REAL,
    polyline TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
);

CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios (email);
CREATE INDEX IF NOT EXISTS idx_rotas_usuario_id ON rotas (usuario_id);

CREATE TABLE IF NOT EXISTS rota_paradas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rota_id INTEGER NOT NULL,
    ordem INTEGER NOT NULL,
    cep TEXT NOT NULL,
    numero TEXT NOT NULL,
    endereco TEXT NOT NULL,
    lat REAL,
    lng REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rota_id) REFERENCES rotas (id)
);

CREATE INDEX IF NOT EXISTS idx_rota_paradas_rota_id ON rota_paradas (rota_id);
