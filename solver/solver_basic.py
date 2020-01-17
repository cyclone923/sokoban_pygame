from game.logic import FLOOR, WALL, WORKER_ON_FLOOR, DOCK, BOX_ON_DOCK, BOX, WORKER_ON_DOCK

class SokobanSolverBasic(object):
    def __init__(self, map):
        self.walls = set()
        self.playabel = set()
        self.docks = set()
        self.init_boxes_loc = set()
        self.init_worker_loc = None
        self.control_mapping = {(1, 0): "DOWN", (-1, 0): "UP", (0, 1): "RIGHT", (0,-1): "LEFT"}

        for i, row in enumerate(map):
            for j, cell in enumerate(row):
                if cell == WALL:
                    self.walls.add((i,j))
                else:
                    self.playabel.add((i,j))
                    if cell == WORKER_ON_FLOOR:
                        assert self.init_worker_loc is None
                        self.init_worker_loc = (i,j)
                    elif cell == WORKER_ON_DOCK:
                        assert self.init_worker_loc is None
                        self.init_worker_loc = (i,j)
                        self.docks.add((i,j))
                    elif cell == DOCK:
                        self.docks.add((i,j))
                    elif cell == BOX_ON_DOCK:
                        self.init_boxes_loc.add((i,j))
                        self.docks.add((i,j))
                    elif cell == BOX:
                        self.init_boxes_loc.add((i,j))
                    else:
                        assert cell == FLOOR
        assert len(self.init_boxes_loc) == len(self.docks)
        self.solver = None

    def get_one_step_move(self, x, y):
        reachabel = [(x-1,y), (x,y-1), (x,y+1), (x+1,y)]
        reachabel = set(filter(lambda t: (t[0], t[1]) not in self.walls, reachabel))
        return reachabel

    def solve_for_one(self):
        pass
