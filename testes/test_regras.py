import unittest

from model import regras
from model.entidades import Disciplina, Horario, Turma

H = Horario.de_texto


def turma(codigo, creditos, *horarios, vagas=10):
    return Turma(codigo, Disciplina(codigo[:3], codigo, creditos), tuple(map(H, horarios)), vagas)


class TestHorario(unittest.TestCase):
    def test_sobreposicao_parcial(self):
        self.assertTrue(H("SEG 08:00-10:00").sobrepoe(H("SEG 09:00-11:00")))

    def test_horarios_encostados_nao_conflitam(self):
        self.assertFalse(H("SEG 08:00-10:00").sobrepoe(H("SEG 10:00-12:00")))

    def test_dias_diferentes_nao_conflitam(self):
        self.assertFalse(H("SEG 08:00-10:00").sobrepoe(H("TER 08:00-10:00")))

    def test_turma_com_varios_horarios(self):
        a = turma("AAA-A", 4, "SEG 08:00-10:00", "QUA 08:00-10:00")
        b = turma("BBB-A", 4, "QUA 09:00-11:00")
        self.assertTrue(a.conflita_com(b))


class TestFuncoes(unittest.TestCase):
    def test_total_creditos(self):
        grade = [turma("AAA-A", 4, "SEG 08:00-10:00"), turma("BBB-A", 2, "TER 08:00-10:00")]
        self.assertEqual(regras.total_creditos(grade), 6)

    def test_conflitos_com(self):
        a = turma("AAA-A", 4, "SEG 08:00-10:00")
        b = turma("BBB-A", 4, "SEG 09:00-11:00")
        c = turma("CCC-A", 4, "TER 08:00-10:00")
        self.assertEqual(regras.conflitos_com(a, [b, c]), [b])

    def test_turmas_com_vaga(self):
        cheia = turma("AAA-A", 4, "SEG 08:00-10:00", vagas=0)
        livre = turma("BBB-A", 4, "TER 08:00-10:00", vagas=5)
        self.assertEqual(regras.turmas_com_vaga([cheia, livre]), [livre])

    def test_remover_repetidos(self):
        self.assertEqual(regras.remover_repetidos([" mat001", "MAT001", "", "fis001"]), ["MAT001", "FIS001"])

    def test_funcao_pura_nao_altera_entrada(self):
        turmas = [turma("AAA-A", 4, "SEG 08:00-10:00", vagas=0)]
        regras.turmas_com_vaga(turmas)
        self.assertEqual(len(turmas), 1)


if __name__ == "__main__":
    unittest.main()
