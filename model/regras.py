def prereqs_faltando(disciplina, aluno):
    return list(filter(lambda p: not aluno.ja_aprovado(p), disciplina.prereqs))


def turmas_com_vaga(turmas):
    return list(filter(lambda t: t.tem_vagas(), turmas))


def total_creditos(turmas):
    return sum(map(lambda t: t.creditos, turmas))


def conflitos_com(turma, grade):
    return list(filter(lambda outra: turma.conflita_com(outra), grade))


def ordenar_por_creditos(disciplinas):
    return sorted(disciplinas, key=lambda d: (-d.creditos, d.codigo))


def remover_repetidos(codigos):
    resultado = []
    for codigo in codigos:
        codigo = codigo.strip().upper()
        if codigo and codigo not in resultado:
            resultado.append(codigo)
    return resultado
