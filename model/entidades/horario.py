from dataclasses import dataclass


@dataclass(frozen=True)
class Horario:
    dia: str
    inicio: str
    fim: str

    @staticmethod
    def de_texto(texto):
        dia, faixa = texto.split()
        inicio, fim = faixa.split("-")
        return Horario(dia, inicio, fim)

    def sobrepoe(self, outro):
        if self.dia != outro.dia:
            return False
        return self.inicio < outro.fim and outro.inicio < self.fim

    def __str__(self):
        return f"{self.dia} {self.inicio}-{self.fim}"
