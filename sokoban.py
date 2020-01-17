from game.game import SokobanGame
from solver.solver_sat import SokobanSolverSAT
from solver.solver_search import SokobanSolverSearch
from solver.solver_search_advanced import SokobanSolverSearchAdvanced
import time

if __name__ == "__main__":
    # game = SokobanGame(51, SokobanSolverSAT, 17) #13s
    # game = SokobanGame(51, SokobanSolverSearch, 17) #0.42s
    # game = SokobanGame(51, SokobanSolverSearchAdvanced, 17) #2.01s

    # game = SokobanGame(52, SokobanSolverSAT, 14) #0.15s
    # game = SokobanGame(52, SokobanSolverSearch, 14) #0.0016s
    # game = SokobanGame(52, SokobanSolverSearchAdvanced, 14) #0.0011s

    # game = SokobanGame(53, SokobanSolverSAT, 27) #2s
    # game = SokobanGame(53, SokobanSolverSearch, 27) #0.0064s
    # game = SokobanGame(53, SokobanSolverSearchAdvanced, 27) #0.0037s

    # game = SokobanGame(54, SokobanSolverSAT, 52) #7954s
    # game = SokobanGame(54, SokobanSolverSearch, 52) #0.043s
    # game = SokobanGame(54, SokobanSolverSearchAdvanced, 52) #0.0433s


    # game = SokobanGame(1, SokobanSolverSearch, 112) # 7.7
    # game = SokobanGame(1, SokobanSolverSearchAdvanced, 112) # 13

    # game = SokobanGame(5)
    # game.play()
    # exit(0)

    do_not_play = [4, 5]
    do_not_play = []

    for level in range(1,55):
        if level not in do_not_play:
            game = SokobanGame(level, SokobanSolverSearch, 500) # 7.7
            game.auto_play(70)
