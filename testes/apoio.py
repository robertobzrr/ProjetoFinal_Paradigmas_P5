from model.dao.aluno_dao import AlunoDAO
from model.dao.conexao import criar_conexao
from model.dao.dados_iniciais import popular_se_vazio
from model.dao.disciplina_dao import DisciplinaDAO
from model.dao.turma_dao import TurmaDAO
from model.planejador import Planejador


def criar_planejador():
    conn = criar_conexao(":memory:")
    disciplina_dao = DisciplinaDAO(conn)
    turma_dao = TurmaDAO(conn, disciplina_dao)
    aluno_dao = AlunoDAO(conn)
    popular_se_vazio(disciplina_dao, turma_dao, aluno_dao)
    return Planejador(disciplina_dao, turma_dao, aluno_dao)
