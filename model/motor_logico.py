class BaseConhecimento:
    def __init__(self, disciplinas, aluno):
        self.prereqs = {d.codigo: list(d.prereqs) for d in disciplinas}
        self.aprovadas = set(aluno.historico)

    # ---------------- Regras ----------------

    def requer(self, codigo):
        resultado = set()
        for prereq in self.prereqs.get(codigo, []):
            resultado.add(prereq)
            resultado.update(self.requer(prereq))
        return resultado

    def pode_cursar(self, codigo):
        if codigo not in self.prereqs or codigo in self.aprovadas:
            return False
        return all(p in self.aprovadas for p in self.prereqs[codigo])

    def faltantes(self, codigo):
        return sorted(p for p in self.requer(codigo) if p not in self.aprovadas)
