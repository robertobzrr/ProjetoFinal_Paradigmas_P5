from model import regras
from model.motor_logico import BaseConhecimento
from model.resultados import Analise, GradeSugerida, ItemGrade, Verificacao


class Planejador:
    def __init__(self, disciplina_dao, turma_dao, aluno_dao):
        self.disciplina_dao = disciplina_dao
        self.turma_dao = turma_dao
        self.aluno_dao = aluno_dao

    # ---------------- Consultas simples ----------------

    def listar_alunos(self):
        return self.aluno_dao.listar_todos()

    def buscar_aluno(self, matricula):
        return self.aluno_dao.buscar(matricula.strip())

    def listar_oferta(self):
        return self.turma_dao.listar_oferta()

    def historico(self, matricula):
        return self.aluno_dao.historico_detalhado(matricula)

    def disciplinas_elegiveis(self, matricula):
        codigos = self.aluno_dao.elegiveis(matricula)
        return [self.disciplina_dao.buscar(codigo) for codigo in codigos]

    # ---------------- Validacao individual ----------------

    def _motor(self, aluno):
        return BaseConhecimento(self.disciplina_dao.listar_todas(), aluno)

    def verificar(self, aluno, codigo):
        codigo = codigo.strip().upper()
        disciplina = self.disciplina_dao.buscar(codigo)
        if disciplina is None:
            return Verificacao(codigo, "?", False, ["Disciplina não cadastrada."])
        if aluno.ja_aprovado(codigo):
            return Verificacao(codigo, disciplina.nome, False, ["O aluno já foi aprovado nesta disciplina."])

        motivos = []

        faltando = regras.prereqs_faltando(disciplina, aluno)
        if faltando:
            motivos.append("Pré-requisitos não aprovados: " + ", ".join(faltando) + ".")
            todas_faltantes = self._motor(aluno).faltantes(codigo)
            motivos.append("Contando a cadeia inteira, ainda faltam: " + ", ".join(todas_faltantes) + ".")

        turmas = self.turma_dao.listar_por_disciplina(codigo)
        com_vaga = regras.turmas_com_vaga(turmas)
        if not turmas:
            motivos.append("Não há turma ofertada neste período.")
        elif not com_vaga:
            motivos.append("Nenhuma turma com vaga.")

        if motivos:
            return Verificacao(codigo, disciplina.nome, False, motivos)

        if disciplina.prereqs:
            motivos.append("Pré-requisitos aprovados: " + ", ".join(disciplina.prereqs) + ".")
        else:
            motivos.append("Não possui pré-requisitos.")
        for turma in com_vaga:
            motivos.append(f"Turma {turma.codigo} [{turma.horarios_texto()}] com {turma.vagas} vagas.")
        return Verificacao(codigo, disciplina.nome, True, motivos)

    # ---------------- Explicacao das desejadas ----------------

    def _alerta_de_horario(self, codigo_a, codigo_b):
        turmas_a = regras.turmas_com_vaga(self.turma_dao.listar_por_disciplina(codigo_a))
        turmas_b = regras.turmas_com_vaga(self.turma_dao.listar_por_disciplina(codigo_b))

        com_choque = []
        sem_choque = []
        for ta in turmas_a:
            for tb in turmas_b:
                if ta.conflita_com(tb):
                    com_choque.append((ta, tb))
                else:
                    sem_choque.append((ta, tb))

        if not com_choque:
            return None
        if not sem_choque:
            ta, tb = com_choque[0]
            return (f"{codigo_a} e {codigo_b} têm choque de horário em todas as turmas "
                    f"({ta.codigo} [{ta.horarios_texto()}] x {tb.codigo} [{tb.horarios_texto()}]). "
                    f"Não podem ficar na mesma grade.")
        ta, tb = sem_choque[0]
        return (f"{codigo_a} e {codigo_b} têm turmas com choque de horário; "
                f"para cursar as duas, use {ta.codigo} + {tb.codigo}.")

    def explicar_desejadas(self, aluno, codigos, limite):
        codigos = regras.remover_repetidos(codigos)
        verificacoes = [self.verificar(aluno, codigo) for codigo in codigos]
        aceitas = [v.codigo for v in verificacoes if v.ok]

        alertas = []
        for i in range(len(aceitas)):
            for j in range(i + 1, len(aceitas)):
                alerta = self._alerta_de_horario(aceitas[i], aceitas[j])
                if alerta:
                    alertas.append(alerta)

        total = sum(self.disciplina_dao.buscar(codigo).creditos for codigo in aceitas)
        if total > limite:
            alertas.append(f"As desejadas que podem ser cursadas somam {total} créditos, "
                           f"acima do limite de {limite}; nem todas cabem no mesmo período.")
        return Analise(verificacoes, alertas)

    # ---------------- Sugestao automatica de grade ----------------

    def _tentar_encaixar(self, codigo, grade, limite, desejada):
        turmas_na_grade = [item.turma for item in grade]
        creditos_atuais = regras.total_creditos(turmas_na_grade)
        descartadas = []

        for turma in regras.turmas_com_vaga(self.turma_dao.listar_por_disciplina(codigo)):
            choques = regras.conflitos_com(turma, turmas_na_grade)
            if choques:
                nomes = ", ".join(t.codigo for t in choques)
                descartadas.append(f"{turma.codigo} [{turma.horarios_texto()}] tem choque com {nomes}.")
            elif creditos_atuais + turma.creditos > limite:
                descartadas.append(f"{turma.codigo} levaria a grade a {creditos_atuais + turma.creditos} "
                                   f"créditos, acima do limite de {limite}.")
            else:
                return ItemGrade(turma, desejada, " ".join(descartadas)), []

        return None, descartadas

    def sugerir_grade(self, aluno, desejadas, limite, completar=True):
        desejadas = regras.remover_repetidos(desejadas)
        grade = []
        fora = []

        for codigo in desejadas:
            verificacao = self.verificar(aluno, codigo)
            if not verificacao.ok:
                fora.append((codigo, verificacao.motivos))
                continue
            item, motivos = self._tentar_encaixar(codigo, grade, limite, desejada=True)
            if item:
                grade.append(item)
            else:
                fora.append((codigo, motivos))

        if completar:
            outras = regras.ordenar_por_creditos(self.disciplinas_elegiveis(aluno.matricula))
            for disciplina in outras:
                if disciplina.codigo in desejadas:
                    continue
                item, _ = self._tentar_encaixar(disciplina.codigo, grade, limite, desejada=False)
                if item:
                    grade.append(item)

        creditos = regras.total_creditos([item.turma for item in grade])
        return GradeSugerida(grade, creditos, limite, fora)

    # ---------------- Inferencia logica ----------------

    def prerequisitos_em_cadeia(self, aluno, codigo):
        codigo = codigo.strip().upper()
        disciplina = self.disciplina_dao.buscar(codigo)
        if disciplina is None:
            return None
        motor = self._motor(aluno)
        return disciplina, sorted(motor.requer(codigo)), motor.faltantes(codigo)
