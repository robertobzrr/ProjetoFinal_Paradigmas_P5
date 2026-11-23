from dataclasses import dataclass


@dataclass(frozen=True)
class Disciplina:
    codigo: str
    nome: str
    creditos: int
    prereqs: tuple = ()

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
