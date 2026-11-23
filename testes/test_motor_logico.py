import unittest

from model.dao.dados_iniciais import ALUNOS, DISCIPLINAS
from model.motor_logico import BaseConhecimento

ANA, BRUNO, CARLA = ALUNOS


class TestMotorLogico(unittest.TestCase):
    def test_requer_e_transitivo(self):
        base = BaseConhecimento(DISCIPLINAS, CARLA)
        self.assertEqual(base.requer("IA001"), {"PRG004", "PRG002", "PRG003", "PRG001", "ALG001", "MAT001"})

    def test_pode_cursar(self):
        base = BaseConhecimento(DISCIPLINAS, BRUNO)
        self.assertTrue(base.pode_cursar("MAT002"))
        self.assertFalse(base.pode_cursar("MAT003"))
        self.assertFalse(base.pode_cursar("MAT001"))

    def test_faltantes(self):
        self.assertEqual(BaseConhecimento(DISCIPLINAS, ANA).faltantes("IA001"), ["PRG004"])
        self.assertEqual(BaseConhecimento(DISCIPLINAS, CARLA).faltantes("MAT003"), ["MAT001", "MAT002"])


if __name__ == "__main__":
    unittest.main()
