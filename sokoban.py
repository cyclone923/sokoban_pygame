from game.game import SokobanGame
from solver.solver_search import SokobanSolverSearch
from solver.solver_sat import SokobanSolverSAT


if __name__ == "__main__":
    data_dir = "experience"

    for level in range(103, 104):
        game = SokobanGame(level, SokobanSolverSAT, 12) # 7.7
        # print("solution ready")
        # input()
        game.auto_play(50)
        # exit(0)
