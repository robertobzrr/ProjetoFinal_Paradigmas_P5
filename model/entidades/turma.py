from dataclasses import dataclass

from model.entidades.disciplina import Disciplina


@dataclass(frozen=True)
class Turma:
    codigo: str
    disciplina: Disciplina
    horarios: tuple = ()
    vagas: int = 0

    @property
    def creditos(self):
        return self.disciplina.creditos

    def tem_vagas(self):
        return self.vagas > 0

    def conflita_com(self, outra):
        return any(h1.sobrepoe(h2) for h1 in self.horarios for h2 in outra.horarios)

    def horarios_texto(self):
        return ", ".join(str(h) for h in self.horarios)

    def __str__(self):
        return f"{self.codigo} ({self.disciplina.nome})"
