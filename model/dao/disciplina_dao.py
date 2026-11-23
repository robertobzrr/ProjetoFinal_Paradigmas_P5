from model.entidades import Disciplina


class DisciplinaDAO:
    def __init__(self, conn):
        self.conn = conn

    def esta_vazio(self):
        return self.conn.execute("SELECT COUNT(*) FROM disciplinas").fetchone()[0] == 0

    def salvar_varias(self, disciplinas):
        with self.conn:
            for d in disciplinas:
                self.conn.execute(
                    "INSERT INTO disciplinas (codigo, nome, creditos) VALUES (?, ?, ?)",
                    (d.codigo, d.nome, d.creditos),
                )
            for d in disciplinas:
                for prereq in d.prereqs:
                    self.conn.execute(
                        "INSERT INTO prereqs (disciplina_codigo, prereq_codigo) VALUES (?, ?)",
                        (d.codigo, prereq),
                    )

    def _prereqs(self, codigo):
        linhas = self.conn.execute(
            "SELECT prereq_codigo FROM prereqs WHERE disciplina_codigo = ? ORDER BY prereq_codigo",
            (codigo,),
        ).fetchall()
        return tuple(linha[0] for linha in linhas)

    def buscar(self, codigo):
        linha = self.conn.execute(
            "SELECT codigo, nome, creditos FROM disciplinas WHERE codigo = ?", (codigo,)
        ).fetchone()
        if linha is None:
            return None
        codigo, nome, creditos = linha
        return Disciplina(codigo, nome, creditos, self._prereqs(codigo))

    def listar_todas(self):
        linhas = self.conn.execute("SELECT codigo FROM disciplinas ORDER BY codigo").fetchall()
        return [self.buscar(linha[0]) for linha in linhas]
