from game.game import SokobanGame
from solver.solver_sat import SokobanSolverSAT
import time

if __name__ == "__main__":
    game = SokobanGame(-1, SokobanSolverSAT, 27) #2s
    # game = SokobanGame(0, SokobanSolverSAT, 52) #7954s
    time0 = time.time()
    solution = game.solver.solve_for_one()
    time1 = time.time()
    print(time1 - time0)
    game.play(solution)