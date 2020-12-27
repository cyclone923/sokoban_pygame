from solver.solver_basic import SokobanSolverBasic
from heapdict import heapdict
import numpy as np
from scipy.optimize import linear_sum_assignment
import os
from solver.search_util.state import GameState


class SokobanSolverSearch(SokobanSolverBasic):
    def __init__(self, map, step_limit, data_dir=None):
        super().__init__(map)
        self.init_game_info = GameState(self.init_boxes_loc, self.init_worker_loc, None)
        self.step_limit = step_limit
        self.solution_history = None

    def win(self, s):
        return s.boxes == self.docks # set equivalence

    def push_box(self, worker, box, all_boxes):# return the new worker postion and new box posistion
        new_worker_and_box = None
        offset_x, offset_y = box.x - worker.x, box.y - worker.y
        assert (offset_x, offset_y) in self.control_mapping
        push_tar = self.Point(box.x + offset_x, box.y + offset_y)
        if push_tar not in self.walls and push_tar not in all_boxes:
            new_worker_and_box = (box, push_tar)
        return new_worker_and_box

    def at_dead_corner(self, box):
        ans = False
        if box not in self.docks:
            x, y = box
            if self.Point(x+1, y) in self.walls or self.Point(x-1, y) in self.walls:
                if self.Point(x, y+1) in self.walls or self.Point(x, y-1) in self.walls:
                    ans = True
        return ans

    def get_seq_controls(self):
        controls = []
        pre_worker = self.solution_history[0]
        assert pre_worker == self.init_worker_loc
        for worker in self.solution_history[1:]:
            offset_x, offset_y = worker.x - pre_worker.x, worker.y - pre_worker.y
            assert (offset_x, offset_y) in self.control_mapping
            controls.append(self.control_mapping[(offset_x, offset_y)])
            pre_worker = worker
        return controls

    def get_data(self, data_dir):
        assert self.solution_history is not None
        time_length = len(self.solution_history)
        n_walls = len(self.walls)
        n_docks = len(self.docks)
        n_boxes = len(self.init_boxes_loc)
        n_woker = 1
        n_point = n_walls + n_docks + n_boxes + n_woker
        n_feature = 4 # wall, box, docks, worker
        n_action = 4

        actions = np.zeros(shape=(time_length-1, n_action))
        scores = np.zeros(shape=(time_length))
        features = np.zeros(shape=(time_length, n_point, n_feature))
        point_cloud = np.zeros(shape=(time_length, n_point, 2))

        all_action = list(self.control_mapping.values())

        cur_boxes = self.init_boxes_loc
        cur_worker = self.init_worker_loc

        for t in range(0, len(self.solution_history)):
            n = 0
            for f, one_set in enumerate([self.walls, self.docks, cur_boxes]):
                for x, y in one_set:
                    features[t, n, f] = 1
                    point_cloud[t, n, 0],  point_cloud[t, n, 1] = x, y
                    n += 1
            point_cloud[t, n, 0], point_cloud[t, n, 1] = cur_worker.x, cur_worker.y
            features[t, n, 3] = 1
            scores[t] = len(self.solution_history) - (t+1)

            if t < len(self.solution_history)-1:
                worker = self.solution_history[t]
                next_worker = self.solution_history[t+1]
                offset_x, offset_y = next_worker.x - worker.x, next_worker.y - worker.y
                a = all_action.index(self.control_mapping[(offset_x, offset_y)])
                actions[t, a] = 1

                if next_worker in cur_boxes: # only update box position when push happens
                    new_worker, new_box = self.push_box(cur_worker, next_worker, cur_boxes)
                    new_boxes = set(cur_boxes)
                    new_boxes.remove(new_worker)
                    new_boxes.add(new_box)
                    cur_boxes = new_boxes
                cur_worker = next_worker
        np.save(os.path.join(data_dir, "points.npy"), point_cloud)
        np.save(os.path.join(data_dir, "features.npy"), features)
        np.save(os.path.join(data_dir, "scores.npy"), scores)
        np.save(os.path.join(data_dir, "actions.npy"), actions)


    def solve_for_one(self):
        assert self.solution_history is None
        self.solution_history = self.search()

    def get_controls(self):
        assert self.solution_history is not None
        return self.get_seq_controls()

    def creat_game_info(self, boxes, worker, parent):
        return GameState(boxes, worker, parent)

    def expand_current_state(self, current):
        # inefficient one-step state expansion, can be improved with inheritance
        x, y = current.worker
        reachable = self.get_one_step_move(x, y)
        successors = []
        for pos in reachable:
            if pos not in current.boxes: # can move
                new_boxes = set(current.boxes)
                child = self.creat_game_info(new_boxes, pos, current)
                successors.append(child)
            else:
                new_worker_and_box = self.push_box(current.worker, pos, current.boxes)
                if new_worker_and_box is not None:
                    new_worker, new_box = new_worker_and_box
                    new_boxes = set(current.boxes)
                    new_boxes.remove(new_worker)
                    new_boxes.add(new_box)
                    child = self.creat_game_info(new_boxes, new_worker, current)
                    successors.append(child)
        return successors

    def search(self):
        frontier = heapdict()
        frontier[self.init_game_info] = self.bfs_evaluate(self.init_game_info)
        solution = None
        expanded = set()
        while frontier.peekitem() and solution is None:
            current, _ = frontier.popitem()
            expanded.add(current)
            successors = self.expand_current_state(current)
            for s in successors:
                if self.win(s):
                    solution = s.get_history()
                    print(f"State Searched {len(expanded)+len(frontier)}")
                    break
                else:
                    if s not in expanded and s not in frontier and not self.is_dead_state(s):
                        score = self.bfs_evaluate(s)
                        frontier[s] = score
        return solution

    def is_dead_state(self, state):
        for box in state.boxes:
            if self.at_dead_corner(box):
                return True
        return False

    def get_depth(self, state):
        d = 0
        while state is not None:
            state = state.parent
            d += 1
        return d

    def bfs_evaluate(self, game_state):# consistent heuristic
        score = self.get_depth(game_state)
        return score

    def random_evaluate(self, game_state):# not consistent heuristic
        return self.get_depth(game_state) + np.random.random()

    def cost_ot_evaluate(self, game_state): # consistent heuristic, lower bound of moves need to be taken
        n_box = len(self.docks)
        cost = np.zeros(shape=(n_box, n_box))
        for i, (x1, y1) in enumerate(self.docks):
            for j, (x2, y2) in enumerate(game_state.boxes):
                cost[i,j] = abs(x1-x2) + abs(y1-y2)
        row_idx, col_idx = linear_sum_assignment(cost)
        return self.get_depth(game_state) + cost[row_idx, col_idx].sum()

    def ot_evaluate(self, game_state): # consistent heuristic, lower bound of moves need to be taken
        n_box = len(self.docks)
        cost = np.zeros(shape=(n_box, n_box))
        for i, (x1, y1) in enumerate(self.docks):
            for j, (x2, y2) in enumerate(game_state.boxes):
                cost[i,j] = abs(x1-x2) + abs(y1-y2)
        row_idx, col_idx = linear_sum_assignment(cost)
        return cost[row_idx, col_idx].sum()











