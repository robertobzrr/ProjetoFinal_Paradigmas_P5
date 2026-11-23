from model.entidades import Aluno, Disciplina, Horario, Turma

DISCIPLINAS = (
    Disciplina("MAT001", "Calculo I", 4),
    Disciplina("MAT002", "Calculo II", 4, ("MAT001",)),
    Disciplina("MAT003", "Calculo III", 4, ("MAT002",)),
    Disciplina("ALG001", "Algebra Linear", 4, ("MAT001",)),
    Disciplina("FIS001", "Fisica I", 4),
    Disciplina("FIS002", "Fisica II", 4, ("FIS001", "MAT001")),
    Disciplina("PRG001", "Introducao a Programacao", 4),
    Disciplina("PRG002", "Estruturas de Dados", 4, ("PRG001",)),
    Disciplina("PRG003", "Programacao Orientada a Objetos", 4, ("PRG001",)),
    Disciplina("PRG004", "Paradigmas de Programacao", 4, ("PRG002", "PRG003")),
    Disciplina("BD001", "Banco de Dados", 4, ("PRG002",)),
    Disciplina("IA001", "Inteligencia Artificial", 4, ("PRG004", "ALG001")),
    Disciplina("EXT001", "Comunicacao e Expressao", 2),
    Disciplina("ETI001", "Etica e Sociedade", 2),
)

_OFERTA = (
    ("MAT001-A", "MAT001", 40, ("SEG 08:00-10:00", "QUA 08:00-10:00")),
    ("MAT002-A", "MAT002", 30, ("TER 08:00-10:00", "QUI 08:00-10:00")),
    ("MAT003-A", "MAT003", 25, ("SEG 10:00-12:00", "QUA 10:00-12:00")),
    ("ALG001-A", "ALG001", 30, ("TER 10:00-12:00", "QUI 10:00-12:00")),
    ("FIS001-A", "FIS001", 30, ("SEG 14:00-16:00", "QUA 14:00-16:00")),
    ("FIS002-A", "FIS002", 20, ("TER 14:00-16:00", "QUI 14:00-16:00")),
    ("PRG001-A", "PRG001", 40, ("SEX 08:00-12:00",)),
    ("PRG002-A", "PRG002", 30, ("TER 15:00-17:00", "QUI 15:00-17:00")),
    ("PRG002-B", "PRG002", 20, ("SEX 14:00-16:00", "SEG 16:00-18:00")),
    ("PRG003-A", "PRG003", 30, ("QUA 16:00-18:00", "SEX 16:00-18:00")),
    ("PRG004-A", "PRG004", 20, ("SEG 19:00-21:00", "QUA 19:00-21:00")),
    ("BD001-A",  "BD001",   0, ("TER 19:00-21:00", "QUI 19:00-21:00")),
    ("IA001-A",  "IA001",  10, ("SEX 19:00-21:00",)),
    ("EXT001-A", "EXT001", 50, ("SEG 10:00-12:00", "QUA 10:00-12:00")),
    ("ETI001-A", "ETI001", 50, ("SEX 10:00-12:00",)),
)

ALUNOS = (
    Aluno("2021001", "Ana Silva", frozenset(
        {"MAT001", "MAT002", "ALG001", "FIS001", "PRG001", "PRG002", "PRG003"})),
    Aluno("2021002", "Bruno Costa", frozenset({"MAT001", "FIS001", "PRG001"})),
    Aluno("2021003", "Carla Mendes", frozenset()),
)


def montar_turmas():
    por_codigo = {d.codigo: d for d in DISCIPLINAS}
    return tuple(
        Turma(cod, por_codigo[disc], tuple(map(Horario.de_texto, horarios)), vagas)
        for cod, disc, vagas, horarios in _OFERTA
    )


def popular_se_vazio(disciplina_dao, turma_dao, aluno_dao):
    if not disciplina_dao.esta_vazio():
        return
    disciplina_dao.salvar_varias(DISCIPLINAS)
    turma_dao.salvar_varias(montar_turmas())
    aluno_dao.salvar_varios(ALUNOS)
