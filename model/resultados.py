from dataclasses import dataclass


@dataclass
class Verificacao:
    codigo: str
    nome: str
    ok: bool
    motivos: list


@dataclass
class Analise:
    verificacoes: list
    alertas: list


@dataclass
class ItemGrade:
    turma: object
    desejada: bool
    observacao: str


@dataclass
class GradeSugerida:
    itens: list
    creditos: int
    limite: int
    fora: list
