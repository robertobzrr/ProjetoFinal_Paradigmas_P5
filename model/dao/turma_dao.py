from model.entidades import Horario, Turma


class TurmaDAO:
    def __init__(self, conn, disciplina_dao):
        self.conn = conn
        self.disciplina_dao = disciplina_dao

    def salvar_varias(self, turmas):
        with self.conn:
            for t in turmas:
                self.conn.execute(
                    "INSERT INTO turmas (codigo, disciplina_codigo, vagas) VALUES (?, ?, ?)",
                    (t.codigo, t.disciplina.codigo, t.vagas),
                )
                for h in t.horarios:
                    self.conn.execute(
                        "INSERT INTO horarios (turma_codigo, dia, inicio, fim) VALUES (?, ?, ?, ?)",
                        (t.codigo, h.dia, h.inicio, h.fim),
                    )

    def _horarios(self, codigo_turma):
        linhas = self.conn.execute(
            "SELECT dia, inicio, fim FROM horarios WHERE turma_codigo = ? ORDER BY rowid",
            (codigo_turma,),
        ).fetchall()
        return tuple(Horario(dia, inicio, fim) for dia, inicio, fim in linhas)

    def _montar_turma(self, linha):
        codigo, codigo_disciplina, vagas = linha
        disciplina = self.disciplina_dao.buscar(codigo_disciplina)
        return Turma(codigo, disciplina, self._horarios(codigo), vagas)

    def listar_oferta(self):
        linhas = self.conn.execute(
            "SELECT codigo, disciplina_codigo, vagas FROM turmas ORDER BY codigo"
        ).fetchall()
        return [self._montar_turma(linha) for linha in linhas]

    def listar_por_disciplina(self, codigo_disciplina):
        linhas = self.conn.execute(
            "SELECT codigo, disciplina_codigo, vagas FROM turmas WHERE disciplina_codigo = ? ORDER BY codigo",
            (codigo_disciplina,),
        ).fetchall()
        return [self._montar_turma(linha) for linha in linhas]
