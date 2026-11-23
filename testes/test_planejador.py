import unittest

from testes.apoio import criar_planejador

LIMITE = 20


class TestPlanejador(unittest.TestCase):
    def setUp(self):
        self.p = criar_planejador()
        self.addCleanup(self.p.disciplina_dao.conn.close)
        self.ana = self.p.buscar_aluno("2021001")
        self.bruno = self.p.buscar_aluno("2021002")
        self.carla = self.p.buscar_aluno("2021003")

    def codigos(self, grade):
        return [i.turma.disciplina.codigo for i in grade.itens]

    # ---- Teste 1 do enunciado ----
    def test_aluno_sem_prerequisito_em_disciplina_avancada(self):
        v = self.p.verificar(self.carla, "IA001")
        self.assertFalse(v.ok)
        self.assertIn("ALG001, PRG004", v.motivos[0])

    def test_prerequisito_na_mesma_proposta_nao_basta(self):
        grade = self.p.sugerir_grade(self.carla, ["MAT001", "MAT002"], LIMITE)
        self.assertIn("MAT001", self.codigos(grade))
        self.assertNotIn("MAT002", self.codigos(grade))

    # ---- Teste 2 do enunciado ----
    def test_desejadas_com_conflito_de_horario(self):
        analise = self.p.explicar_desejadas(self.ana, ["MAT003", "EXT001"], LIMITE)
        self.assertTrue(any("choque" in a for a in analise.alertas))
        grade = self.p.sugerir_grade(self.ana, ["MAT003", "EXT001"], LIMITE)
        self.assertIn("MAT003", self.codigos(grade))
        self.assertEqual([c for c, _ in grade.fora], ["EXT001"])

    # ---- Teste 3 do enunciado ----
    def test_grade_nao_ultrapassa_limite(self):
        desejadas = ["MAT002", "ALG001", "FIS002", "PRG002", "PRG003", "EXT001"]
        grade = self.p.sugerir_grade(self.bruno, desejadas, LIMITE)
        self.assertLessEqual(grade.creditos, LIMITE)
        self.assertEqual(len(grade.itens), 5)
        self.assertIn("acima do limite", grade.fora[0][1][0])

    # ---- Teste 4 do enunciado ----
    def test_varias_alternativas_escolha_explicada(self):
        grade = self.p.sugerir_grade(self.bruno, ["FIS002", "PRG002"], LIMITE)
        turmas = {i.turma.codigo: i for i in grade.itens}
        self.assertIn("PRG002-B", turmas)
        self.assertIn("PRG002-A", turmas["PRG002-B"].observacao)
        self.assertFalse(grade.fora)

    # ---- Regras extras ----
    def test_grade_sem_choque_de_horario(self):
        for aluno in (self.ana, self.bruno, self.carla):
            turmas = [i.turma for i in self.p.sugerir_grade(aluno, [], LIMITE).itens]
            for i, a in enumerate(turmas):
                for b in turmas[i + 1:]:
                    self.assertFalse(a.conflita_com(b))

    def test_nao_sugere_disciplina_ja_aprovada(self):
        grade = self.p.sugerir_grade(self.ana, ["PRG002"], LIMITE)
        self.assertNotIn("PRG002", self.codigos(grade))

    def test_turma_sem_vagas(self):
        v = self.p.verificar(self.ana, "BD001")
        self.assertFalse(v.ok)
        self.assertIn("Nenhuma turma com vaga", v.motivos[0])

    def test_sql_e_python_concordam_nas_elegiveis(self):
        for aluno in (self.ana, self.bruno, self.carla):
            via_sql = {d.codigo for d in self.p.disciplinas_elegiveis(aluno.matricula)}
            via_python = {d.codigo for d in self.p.disciplina_dao.listar_todas()
                          if self.p.verificar(aluno, d.codigo).ok}
            self.assertEqual(via_sql, via_python)


if __name__ == "__main__":
    unittest.main()
