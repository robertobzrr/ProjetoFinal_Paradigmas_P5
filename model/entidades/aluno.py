from dataclasses import dataclass


@dataclass(frozen=True)
class Aluno:
    matricula: str
    nome: str
    historico: frozenset = frozenset()

    def ja_aprovado(self, codigo_disciplina):
        return codigo_disciplina in self.historico

    def __str__(self):
        return f"{self.nome} ({self.matricula})"
