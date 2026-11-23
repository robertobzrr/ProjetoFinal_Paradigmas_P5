class PlanejadorController:
    def __init__(self, planejador, view, limite_padrao):
        self.planejador = planejador
        self.view = view
        self.limite_padrao = limite_padrao

    def executar(self):
        while True:
            self.view.mostrar_menu()
            opcao = self.view.ler_opcao()

            if opcao == "0":
                self.view.mensagem("Até logo!")
                break
            elif opcao == "1":
                self.listar_oferta()
            elif opcao == "2":
                self.consultar_historico()
            elif opcao == "3":
                self.explicar_desejadas()
            elif opcao == "4":
                self.sugerir_grade()
            elif opcao == "5":
                self.listar_elegiveis()
            elif opcao == "6":
                self.mostrar_prerequisitos()
            elif opcao == "7":
                self.demonstracao()
            else:
                self.view.erro("Opção inválida.")

    def _ler_aluno(self):
        matricula = self.view.ler_matricula(self.planejador.listar_alunos())
        aluno = self.planejador.buscar_aluno(matricula)
        if aluno is None:
            self.view.erro("Aluno não encontrado.")
        return aluno

    # ---------------- Opcoes do menu ----------------

    def listar_oferta(self):
        self.view.mostrar_oferta(self.planejador.listar_oferta())

    def consultar_historico(self):
        aluno = self._ler_aluno()
        if aluno:
            self.view.mostrar_historico(aluno, self.planejador.historico(aluno.matricula))

    def explicar_desejadas(self):
        aluno = self._ler_aluno()
        if not aluno:
            return
        codigos = self.view.ler_codigos()
        if not codigos:
            self.view.erro("Nenhum código informado.")
            return
        limite = self.view.ler_limite(self.limite_padrao)
        analise = self.planejador.explicar_desejadas(aluno, codigos, limite)
        self.view.mostrar_analise(aluno, analise, limite)

    def sugerir_grade(self):
        aluno = self._ler_aluno()
        if not aluno:
            return
        codigos = self.view.ler_codigos()
        limite = self.view.ler_limite(self.limite_padrao)
        completar = self.view.ler_sim_nao("Completar a grade com outras disciplinas elegíveis?")
        grade = self.planejador.sugerir_grade(aluno, codigos, limite, completar)
        self.view.mostrar_grade(aluno, grade)

    def listar_elegiveis(self):
        aluno = self._ler_aluno()
        if aluno:
            self.view.mostrar_elegiveis(aluno, self.planejador.disciplinas_elegiveis(aluno.matricula))

    def mostrar_prerequisitos(self):
        aluno = self._ler_aluno()
        if not aluno:
            return
        resultado = self.planejador.prerequisitos_em_cadeia(aluno, self.view.ler_codigo())
        if resultado is None:
            self.view.erro("Disciplina não cadastrada.")
            return
        disciplina, requer, faltantes = resultado
        self.view.mostrar_prerequisitos(aluno, disciplina, requer, faltantes)

    # ---------------- Demonstracao ----------------

    def demonstracao(self):
        limite = self.limite_padrao
        ana = self.planejador.buscar_aluno("2021001")
        bruno = self.planejador.buscar_aluno("2021002")
        carla = self.planejador.buscar_aluno("2021003")

        self.view.titulo("TESTE 1 - Aluno sem pré-requisito tenta disciplina avançada")
        self.view.mensagem("Carla (histórico vazio) quer IA001 e, na mesma proposta, MAT001 + MAT002.")
        analise = self.planejador.explicar_desejadas(carla, ["IA001", "MAT001", "MAT002"], limite)
        self.view.mostrar_analise(carla, analise, limite)
        self.view.mensagem("→ MAT002 continua bloqueada mesmo com MAT001 na mesma proposta:")
        self.view.mensagem("  o pré-requisito precisa estar APROVADO no histórico.")
        disciplina, requer, faltantes = self.planejador.prerequisitos_em_cadeia(carla, "IA001")
        self.view.mostrar_prerequisitos(carla, disciplina, requer, faltantes)
        self.view.pausar()

        self.view.titulo("TESTE 2 - Duas disciplinas desejadas com choque de horário")
        self.view.mensagem("Ana quer MAT003 e EXT001 (ambas SEG/QUA 10:00-12:00).")
        desejadas = ["MAT003", "EXT001"]
        self.view.mostrar_analise(ana, self.planejador.explicar_desejadas(ana, desejadas, limite), limite)
        self.view.mostrar_grade(ana, self.planejador.sugerir_grade(ana, desejadas, limite))
        self.view.pausar()

        self.view.titulo(f"TESTE 3 - Grade ultrapassaria o limite de {limite} créditos")
        desejadas = ["MAT002", "ALG001", "FIS002", "PRG002", "PRG003", "EXT001"]
        self.view.mensagem(f"Bruno quer {', '.join(desejadas)} (22 créditos).")
        self.view.mostrar_analise(bruno, self.planejador.explicar_desejadas(bruno, desejadas, limite), limite)
        self.view.mostrar_grade(bruno, self.planejador.sugerir_grade(bruno, desejadas, limite))
        self.view.pausar()

        self.view.titulo("TESTE 4 - Várias alternativas: escolha válida e explicável")
        self.view.mensagem("Bruno quer FIS002 e PRG002. PRG002 tem duas turmas; a PRG002-A choca com FIS002-A.")
        desejadas = ["FIS002", "PRG002"]
        self.view.mostrar_analise(bruno, self.planejador.explicar_desejadas(bruno, desejadas, limite), limite)
        self.view.mostrar_grade(bruno, self.planejador.sugerir_grade(bruno, desejadas, limite))
        self.view.titulo("FIM DA DEMONSTRAÇÃO")
