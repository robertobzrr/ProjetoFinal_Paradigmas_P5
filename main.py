from config import LIMITE_CREDITOS_PADRAO
from controller.planejador_controller import PlanejadorController
from model.dao.aluno_dao import AlunoDAO
from model.dao.conexao import criar_conexao
from model.dao.dados_iniciais import popular_se_vazio
from model.dao.disciplina_dao import DisciplinaDAO
from model.dao.turma_dao import TurmaDAO
from model.planejador import Planejador
from view.terminal_view import TerminalView


def main():
    conn = criar_conexao()
    disciplina_dao = DisciplinaDAO(conn)
    turma_dao = TurmaDAO(conn, disciplina_dao)
    aluno_dao = AlunoDAO(conn)
    popular_se_vazio(disciplina_dao, turma_dao, aluno_dao)

    planejador = Planejador(disciplina_dao, turma_dao, aluno_dao)
    controller = PlanejadorController(planejador, TerminalView(), LIMITE_CREDITOS_PADRAO)
    try:
        controller.executar()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
