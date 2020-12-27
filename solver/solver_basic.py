from game.logic import FLOOR, WALL, WORKER_ON_FLOOR, DOCK, BOX_ON_DOCK, BOX, WORKER_ON_DOCK
from collections import namedtuple

class SokobanSolverBasic(object):
    def __init__(self, map):
        self.walls = set()
        self.playabel = set()
        self.docks = set()
        self.init_boxes_loc = set()
        self.init_worker_loc = None
        self.control_mapping = {(1, 0): "DOWN", (-1, 0): "UP", (0, 1): "RIGHT", (0,-1): "LEFT"}
        self.Point = namedtuple("Point", ["x", "y"])

        for i, row in enumerate(map):
            for j, cell in enumerate(row):
                if cell == WALL:
                    self.walls.add(self.Point(i,j))
                else:
                    self.playabel.add(self.Point(i,j))
                    if cell == WORKER_ON_FLOOR:
                        assert self.init_worker_loc is None
                        self.init_worker_loc = (self.Point(i,j))
                    elif cell == WORKER_ON_DOCK:
                        assert self.init_worker_loc is None
                        self.init_worker_loc = (self.Point(i,j))
                        self.docks.add(self.Point(i,j))
                    elif cell == DOCK:
                        self.docks.add(self.Point(i,j))
                    elif cell == BOX_ON_DOCK:
                        self.init_boxes_loc.add(self.Point(i,j))
                        self.docks.add(self.Point(i,j))
                    elif cell == BOX:
                        self.init_boxes_loc.add(self.Point(i,j))
                    else:
                        assert cell == FLOOR
        assert len(self.init_boxes_loc) == len(self.docks)
        self.solver = None

    def get_one_step_move(self, x, y):
        reachabel = [self.Point(x-1,y), self.Point(x,y-1), self.Point(x,y+1), self.Point(x+1,y)]
        reachabel = set(filter(lambda point: (point.x, point.y) not in self.walls, reachabel))
        return reachabel

    def solve_for_one(self):
        pass
