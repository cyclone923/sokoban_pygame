from solver.solver_basic import SokobanSolverBasic
from queue import Queue
from heapdict import heapdict
import time

class GameState(object):
    def __init__(self, boxes, worker, parent):
        self.boxes = boxes
        self.worker = worker
        self.parent = parent

    def __eq__(self, other):
        return self.boxes == other.boxes and self.worker == other.worker

    def __hash__(self):
        return hash( (self.worker, frozenset(self.boxes)))

    def get_history(self):
        history = []
        current = self
        while current is not None:
            history.append((current.worker, current.boxes))
            current = current.parent
        history.reverse()
        return history


class SokobanSolverSearch(SokobanSolverBasic):
    def __init__(self, map, step_limit):
        super().__init__(map)
        self.init_game_info = GameState(self.init_boxes_loc, self.init_worker_loc, None)
        self.goal_game_state = GameState(self.docks, None, None)
        self.step_limit = step_limit

    def win(self, s):
        return s.boxes == self.goal_game_state.boxes # set equivalence

    def push_box(self, worker, box, all_boxes):# return the new worker postion and new box posistion
        new_worker_and_box = None
        offset_x, offset_y = box[0] - worker[0], box[1] - worker[1]
        assert (offset_x, offset_y) in self.control_mapping
        push_tar = (box[0] + offset_x, box[1] + offset_y)
        if push_tar not in self.walls and push_tar not in all_boxes:
            new_worker_and_box = (box, push_tar)
        return new_worker_and_box

    def at_dead_corner(self, box):
        ans = False
        if box not in self.docks:
            x, y = box
            if (x+1, y) in self.walls or (x-1, y) in self.walls:
                if (x, y+1) in self.walls or (x, y-1) in self.walls:
                    ans = True
        return ans

    def bfs_for_path(self, init_worker, tar_worker, boxes):
        my_queue = Queue()
        my_queue.put((init_worker, None))
        solution = None
        memory = set()
        memory.add(init_worker)
        while not my_queue.empty() and solution is None:
            current = my_queue.get()
            worker, _ = current
            one_step_tars = self.get_one_step_move(worker[0], worker[1])
            one_step_tars = set(filter(lambda x: x not in boxes and x not in memory, one_step_tars))
            for new_worker in one_step_tars:
                if new_worker == tar_worker:
                    solution = (tar_worker, current)
                    break
                else:
                    if new_worker not in memory:
                        my_queue.put((new_worker, current))
                        memory.add(new_worker)
        seq_moves = []
        while solution is not None:
            seq_moves.append(solution[0])
            solution = solution[1]
        return list(reversed(seq_moves))

    def get_seq_controls(self, history):
        controls = []
        pre_worker, pre_boxes = history[0][0], history[0][1]
        assert pre_worker == self.init_worker_loc
        assert pre_boxes == self.init_boxes_loc
        for worker, boxes in history[1:]:
            offset_x, offset_y = worker[0] - pre_worker[0], worker[1] - pre_worker[1]
            if (offset_x, offset_y) in self.control_mapping:
                controls.append(self.control_mapping[(offset_x, offset_y)])
            else:
                moves = self.bfs_for_path(pre_worker, worker, pre_boxes)
                pre_x, pre_y = moves[0]
                for x, y in moves[1:]:
                    offset_x, offset_y = x - pre_x, y - pre_y
                    controls.append(self.control_mapping[(offset_x, offset_y)])
                    pre_x = x
                    pre_y = y
            pre_worker = worker
            pre_boxes = boxes
        return controls

    def solve_for_one(self):
        history = self.search()
        control = None
        if history is not None:
            control = self.get_seq_controls(history)
            # print(control)
        else:
            print(f"No solution found in {self.step_limit} steps")
        return control

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
                new_worker_and_box = self.push_box((x,y), pos, current.boxes)
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
        frontier[self.init_game_info] = self.evaluate(self.init_game_info)
        solution = None
        expanded = set()
        while frontier.peekitem() and solution is None:
            current, _ = frontier.popitem()
            expanded.add(current)
            successors = self.expand_current_state(current)
            for s in successors:
                if self.win(s):
                    solution = s.get_history()
                    break
                else:
                    if s not in expanded and s not in frontier:
                        score = self.evaluate(s)
                        if score != float('inf'):
                            frontier[s] = score
        return solution

    def get_depth(self, state):
        d = 0
        while state is not None:
            state = state.parent
            d += 1
        return d

    def evaluate(self, game_state):
        # score = 1
        score = self.get_depth(game_state)
        for box in game_state.boxes:
            if self.at_dead_corner(box):
                score += float('inf')
                break
        return score








