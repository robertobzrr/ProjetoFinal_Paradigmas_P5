from model.entidades import Aluno


class AlunoDAO:
    def __init__(self, conn):
        self.conn = conn

    def salvar_varios(self, alunos):
        with self.conn:
            for a in alunos:
                self.conn.execute(
                    "INSERT INTO alunos (matricula, nome) VALUES (?, ?)",
                    (a.matricula, a.nome),
                )
                for codigo in a.historico:
                    self.conn.execute(
                        "INSERT INTO historico (matricula, disciplina_codigo) VALUES (?, ?)",
                        (a.matricula, codigo),
                    )

    def _historico(self, matricula):
        linhas = self.conn.execute(
            "SELECT disciplina_codigo FROM historico WHERE matricula = ?", (matricula,)
        ).fetchall()
        return frozenset(linha[0] for linha in linhas)

    def buscar(self, matricula):
        linha = self.conn.execute(
            "SELECT matricula, nome FROM alunos WHERE matricula = ?", (matricula,)
        ).fetchone()
        if linha is None:
            return None
        matricula, nome = linha
        return Aluno(matricula, nome, self._historico(matricula))

    def listar_todos(self):
        linhas = self.conn.execute("SELECT matricula FROM alunos ORDER BY matricula").fetchall()
        return [self.buscar(linha[0]) for linha in linhas]

    # ---------- Consultas declarativas (SQL) ----------

    def historico_detalhado(self, matricula):
        return self.conn.execute("""
            SELECT d.codigo, d.nome, d.creditos
            FROM historico h
            JOIN disciplinas d ON d.codigo = h.disciplina_codigo
            WHERE h.matricula = ?
            ORDER BY d.codigo
        """, (matricula,)).fetchall()

    def elegiveis(self, matricula):
        linhas = self.conn.execute("""
            SELECT d.codigo
            FROM disciplinas d
            WHERE NOT EXISTS (
                    SELECT 1 FROM historico h
                    WHERE h.matricula = :m AND h.disciplina_codigo = d.codigo)
              AND NOT EXISTS (
                    SELECT 1 FROM prereqs p
                    WHERE p.disciplina_codigo = d.codigo
                      AND NOT EXISTS (
                            SELECT 1 FROM historico h
                            WHERE h.matricula = :m AND h.disciplina_codigo = p.prereq_codigo))
              AND EXISTS (
                    SELECT 1 FROM turmas t
                    WHERE t.disciplina_codigo = d.codigo AND t.vagas > 0)
            ORDER BY d.codigo
        """, {"m": matricula}).fetchall()
        return tuple(l[0] for l in linhas)
