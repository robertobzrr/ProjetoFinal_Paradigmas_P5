import sqlite3

from config import DB_PATH

ESQUEMA = """
CREATE TABLE IF NOT EXISTS disciplinas (
    codigo   TEXT PRIMARY KEY,
    nome     TEXT NOT NULL,
    creditos INTEGER NOT NULL CHECK (creditos > 0)
);

CREATE TABLE IF NOT EXISTS prereqs (
    disciplina_codigo TEXT NOT NULL REFERENCES disciplinas(codigo),
    prereq_codigo     TEXT NOT NULL REFERENCES disciplinas(codigo),
    PRIMARY KEY (disciplina_codigo, prereq_codigo)
);

CREATE TABLE IF NOT EXISTS turmas (
    codigo            TEXT PRIMARY KEY,
    disciplina_codigo TEXT NOT NULL REFERENCES disciplinas(codigo),
    vagas             INTEGER NOT NULL CHECK (vagas >= 0)
);

CREATE TABLE IF NOT EXISTS horarios (
    turma_codigo TEXT NOT NULL REFERENCES turmas(codigo),
    dia          TEXT NOT NULL,
    inicio       TEXT NOT NULL,
    fim          TEXT NOT NULL,
    CHECK (inicio < fim)
);

CREATE TABLE IF NOT EXISTS alunos (
    matricula TEXT PRIMARY KEY,
    nome      TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS historico (
    matricula         TEXT NOT NULL REFERENCES alunos(matricula),
    disciplina_codigo TEXT NOT NULL REFERENCES disciplinas(codigo),
    PRIMARY KEY (matricula, disciplina_codigo)
);
"""


def criar_conexao(caminho=DB_PATH):
    conn = sqlite3.connect(caminho)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(ESQUEMA)
    return conn
