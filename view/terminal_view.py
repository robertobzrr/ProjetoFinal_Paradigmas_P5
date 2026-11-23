OPCOES_MENU = (
    ("1", "Listar oferta de turmas"),
    ("2", "Consultar histórico de um aluno"),
    ("3", "Explicar disciplinas desejadas"),
    ("4", "Sugerir grade automática"),
    ("5", "Listar disciplinas elegíveis (consulta SQL)"),
    ("6", "Cadeia de pré-requisitos (motor lógico)"),
    ("7", "Demonstração dos testes do enunciado"),
    ("0", "Sair"),
)

ESTRATEGIA = ("Estratégia: entram primeiro as desejadas, na ordem informada; "
              "depois as demais elegíveis, das de mais créditos para as de menos.")


class TerminalView:
    # ---------------- Entrada ----------------

    def ler(self, rotulo, se_fim=""):
        try:
            return input(f"{rotulo}: ").strip()
        except EOFError: 
            print()
            return se_fim

    def ler_opcao(self):
        return self.ler("\nEscolha uma opção", se_fim="0")

    def ler_matricula(self, alunos):
        print("  Alunos: " + " | ".join(f"{a.matricula} {a.nome}" for a in alunos))
        return self.ler("Matrícula do aluno")

    def ler_codigos(self):
        texto = self.ler("Códigos das disciplinas (separados por vírgula)")
        return [c.strip().upper() for c in texto.split(",") if c.strip()]

    def ler_codigo(self):
        return self.ler("Código da disciplina").upper()

    def ler_limite(self, padrao):
        texto = self.ler(f"Limite de créditos [Enter = {padrao}]")
        if not texto:
            return padrao
        if texto.isdigit() and int(texto) > 0:
            return int(texto)
        self.erro(f"Valor inválido; usando {padrao}.")
        return padrao

    def ler_sim_nao(self, pergunta, padrao=True):
        texto = self.ler(f"{pergunta} [{'S/n' if padrao else 's/N'}]").lower()
        return padrao if not texto else texto.startswith("s")

    def pausar(self):
        self.ler("\n(Enter para continuar)")

    # ---------------- Saida generica ----------------

    def mostrar_menu(self):
        print("\n" + "=" * 52)
        print("   PLANEJADOR DE MATRÍCULA ACADÊMICA")
        print("=" * 52)
        for chave, texto in OPCOES_MENU:
            print(f"  {chave}. {texto}")

    def titulo(self, texto):
        print(f"\n--- {texto} ---")

    def mensagem(self, texto):
        print(f"  {texto}")

    def erro(self, texto):
        print(f"  [!] {texto}")

    # ---------------- Saidas especificas ----------------

    def mostrar_oferta(self, turmas):
        self.titulo("Oferta de turmas")
        print(f"  {'Turma':<9} {'Disciplina':<33} {'Cr':>2} {'Vagas':>5}  {'Horários':<34} Pré-requisitos")
        for t in turmas:
            pre = ", ".join(t.disciplina.prereqs) or "-"
            print(f"  {t.codigo:<9} {t.disciplina.nome:<33} {t.creditos:>2} {t.vagas:>5}  "
                  f"{t.horarios_texto():<34} {pre}")

    def mostrar_historico(self, aluno, linhas):
        self.titulo(f"Histórico de {aluno}")
        if not linhas:
            self.mensagem("Nenhuma disciplina aprovada ainda.")
            return
        for codigo, nome, creditos in linhas:
            self.mensagem(f"{codigo:<7} {nome:<33} {creditos} cr")
        self.mensagem(f"Total: {len(linhas)} disciplinas, {sum(l[2] for l in linhas)} créditos")

    def _mostrar_verificacao(self, v):
        status = "PODE CURSAR" if v.ok else "NÃO PODE"
        print(f"  {v.codigo} - {v.nome}: [{status}]")
        for motivo in v.motivos:
            print(f"      • {motivo}")

    def mostrar_analise(self, aluno, analise, limite):
        self.titulo(f"Análise das desejadas de {aluno} (limite {limite} créditos)")
        for v in analise.verificacoes:
            self._mostrar_verificacao(v)
        if analise.alertas:
            print("  Alertas entre as desejadas:")
            for alerta in analise.alertas:
                print(f"      ⚠ {alerta}")

    def mostrar_grade(self, aluno, grade):
        self.titulo(f"Grade sugerida para {aluno}: {grade.creditos}/{grade.limite} créditos")
        self.mensagem(ESTRATEGIA)
        if not grade.itens:
            self.mensagem("Nenhuma disciplina pôde ser incluída.")
        for item in grade.itens:
            t = item.turma
            marca = "desejada" if item.desejada else "sugerida"
            print(f"  [{marca:<8}] {t.codigo:<9} {t.disciplina.nome:<33} {t.creditos} cr  {t.horarios_texto()}")
            if item.observacao:
                print(f"               ↳ {item.observacao}")
        if grade.fora:
            print("  Desejadas que ficaram de fora:")
            for codigo, motivos in grade.fora:
                print(f"    {codigo}:")
                for motivo in motivos:
                    print(f"      • {motivo}")

    def mostrar_elegiveis(self, aluno, disciplinas):
        self.titulo(f"Disciplinas elegíveis para {aluno} (consulta SQL)")
        if not disciplinas:
            self.mensagem("Nenhuma disciplina elegível no momento.")
        for d in disciplinas:
            self.mensagem(f"{d.codigo:<7} {d.nome:<33} {d.creditos} cr")

    def mostrar_prerequisitos(self, aluno, disciplina, requer, faltantes):
        self.titulo(f"Inferência lógica: {disciplina} para {aluno}")
        self.mensagem("Exige (direta ou indiretamente): " + (", ".join(requer) or "nada"))
        if aluno.ja_aprovado(disciplina.codigo):
            self.mensagem("O aluno já foi aprovado nesta disciplina.")
        elif not faltantes:
            self.mensagem("Todos os pré-requisitos estão aprovados: PODE CURSAR.")
        else:
            self.mensagem("Ainda faltam: " + ", ".join(faltantes))
