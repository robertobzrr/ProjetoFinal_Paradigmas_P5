# Planejador de Matrícula Acadêmica — Grupo 3

Programa de terminal que valida matrículas e sugere grades de disciplinas,
**explicando** cada decisão: pré-requisitos (inclusive em cadeia), vagas, choque de
horário e limite de créditos por período. Os dados ficam em SQLite.

## Instalação e execução

Requer apenas **Python 3.8+**. Não há dependências externas (`sqlite3` e `unittest` já vêm com o Python).

```bash
python3 main.py                                   # abre o menu
python3 -m unittest discover -s testes -t . -v    # roda os testes automatizados
```

Na primeira execução é criado o arquivo `planejador.db` com os dados fictícios.
Para recomeçar do zero, basta apagar esse arquivo.

A opção **7 do menu** roda os 4 testes de demonstração pedidos no enunciado.

## Arquitetura (MVC)

```
main.py                  monta Model + View + Controller e inicia
config.py                limite de créditos padrão e caminho do banco
model/
  entidades/             Aluno, Disciplina, Turma, Horario (POO)
  dao/                   conexão, tabelas e consultas SQL (declarativo)
    dados_iniciais.py    dados fictícios: 14 disciplinas, 15 turmas, 3 alunos
  regras.py              funções puras: filtros, soma de créditos, ordenação (funcional)
  motor_logico.py        fatos e regras de pré-requisitos (lógico)
  planejador.py          classe Planejador: valida, explica e sugere grade
  resultados.py          objetos de resposta (Verificacao, Analise, ItemGrade, GradeSugerida)
view/terminal_view.py    único lugar com print/input
controller/              laço do menu: lê a opção, chama o Model e manda o resultado à View
testes/                  unittest com os cenários do enunciado
```

- **Model**: dados e regras de negócio. Não imprime nada.
- **View**: só exibe e lê. Não decide nada.
- **Controller**: liga os dois. Não tem SQL nem formatação.

## Regras de validação

Uma disciplina pode ser cursada quando:
1. o aluno **ainda não foi aprovado** nela;
2. **todos os pré-requisitos estão aprovados no histórico**. Não basta estarem na mesma proposta;
3. existe **ao menos uma turma com vaga**.

Na grade, nenhuma turma pode ter **choque de horário** com outra (uma turma tem vários
horários por semana), e a soma de créditos não pode passar do **limite** (padrão: 20).

## Estratégia de priorização

A estratégia é **gulosa por ordem de preferência** (`Planejador.sugerir_grade`):

1. As **disciplinas desejadas** entram primeiro, **na ordem em que o aluno informou**:
   a primeira da lista tem mais prioridade.
2. Para cada uma, o sistema testa as turmas com vaga e escolhe a **primeira que não tem choque
   de horário** com a grade e **não passa do limite de créditos**.
3. Se o aluno quiser, as vagas restantes são completadas com **outras disciplinas elegíveis**,
   começando pelas de **mais créditos**.

Cada resultado vem explicado. Para cada turma escolhida, o sistema diz por que as turmas
anteriores da mesma disciplina foram descartadas. Para cada desejada que ficou de fora, diz o
motivo: pré-requisito, vaga, choque com qual turma ou limite de créditos.

**Por que gulosa?** É simples de entender e de explicar, e respeita a preferência do aluno.
A limitação é que uma desejada do começo da lista pode ocupar o horário de outras. O
algoritmo não volta atrás para testar outra combinação, então nem sempre encaixa o
**máximo** possível de desejadas. Nesse caso, o aluno pode reordenar a lista.

## Dados fictícios e cenários de teste

| Aluno | Matrícula | Aprovadas |
|---|---|---|
| Ana Silva | 2021001 | MAT001, MAT002, ALG001, FIS001, PRG001, PRG002, PRG003 |
| Bruno Costa | 2021002 | MAT001, FIS001, PRG001 |
| Carla Mendes | 2021003 | nenhuma |

| Teste do enunciado | Cenário |
|---|---|
| Aluno sem pré-requisito em disciplina avançada | Carla pede IA001: o sistema mostra os pré-requisitos diretos que faltam e, pelo motor lógico, toda a cadeia (6 disciplinas). Pede também MAT001 + MAT002: MAT002 continua bloqueada. |
| Duas desejadas com choque de horário | Ana pede MAT003 e EXT001 (SEG/QUA 10–12). |
| Grade ultrapassaria o limite | Bruno pede 22 créditos com limite 20. EXT001 fica de fora, com o motivo. |
| Várias alternativas | Bruno pede FIS002 e PRG002: a turma PRG002-A choca com FIS002-A, então é escolhida a PRG002-B, com a explicação. |

## Paradigmas no projeto

| Paradigma | Onde | Por que essa escolha |
|---|---|---|
| **Imperativo / estruturado** | `controller/planejador_controller.py` → `executar()` e `model/planejador.py` → `sugerir_grade()` | O menu é um laço `while` com `if/elif`, e a montagem da grade é um `for` que acrescenta turmas passo a passo. É a forma mais direta de descrever "faça isto, depois aquilo". |
| **Orientação a objetos** | `model/entidades/` (`Aluno`, `Disciplina`, `Turma`, `Horario`) e `model/planejador.py` (`Planejador`) | Cada conceito do problema vira uma classe com seus dados e comportamentos (`Turma.conflita_com`, `Aluno.ja_aprovado`). O `Planejador` recebe os DAOs no construtor (injeção de dependência), o que permite testá-lo com banco em memória. |
| **Funcional** | `model/regras.py` (`prereqs_faltando`, `turmas_com_vaga`, `total_creditos`, `conflitos_com`, `ordenar_por_creditos`) | Funções puras com `filter`, `map`, `sorted` e `lambda`, sobre entidades imutáveis (`frozen=True`). Elas não alteram a lista recebida, só devolvem uma nova. Por isso o resultado é previsível e fácil de testar. |
| **Declarativo** | `model/dao/conexao.py` (esquema com `CHECK`, `PRIMARY KEY`, `REFERENCES`) e `model/dao/aluno_dao.py` → `elegiveis()`, `historico_detalhado()` | Em SQL descrevemos *o que* queremos ("disciplinas sem pré-requisito pendente e com turma com vaga"), não *como* percorrer os dados. Um teste confirma que essa consulta dá o mesmo resultado da validação em Python. |
| **Lógico** | `model/motor_logico.py` (`BaseConhecimento`: fatos `prereqs` e `aprovadas`; regras `requer`, `pode_cursar`, `faltantes`) | Elegibilidade é naturalmente um conjunto de fatos e regras. A regra recursiva `requer` infere toda a cadeia de pré-requisitos, como faria em Prolog: `requer(D,X) :- prereq(D,X).` e `requer(D,X) :- prereq(D,Y), requer(Y,X).` |
