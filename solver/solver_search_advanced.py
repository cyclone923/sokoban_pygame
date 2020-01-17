from solver.solver_search import SokobanSolverSearch


class SokobanSolverSearchAdvanced(SokobanSolverSearch):
    def __init__(self, map, step_limit):
        super().__init__(map, step_limit)

    def get_reachabel_without_push(self, loc, boxes, visited):
        one_step_tars = self.get_one_step_move(loc[0], loc[1])
        one_step_tars = set(filter(lambda x: x not in boxes and x not in visited, one_step_tars))
        visited = visited.union(one_step_tars)
        for loc in one_step_tars:
            visited = visited.union(self.get_reachabel_without_push(loc, boxes, visited))
        return visited

    def get_move_behavior(self, current):
        # according to current game state, select next reachable push point and push the box
        connected = set()
        init_worker = current.get_worker_loc()
        boxes = current.get_boxes_loc()
        connected.add(init_worker)
        connected = self.get_reachabel_without_push(init_worker, boxes, connected)
        move_behavior = set()
        for box in boxes:
            for one_loc in self.get_one_step_move(box[0], box[1]):
                if one_loc in connected:
                    new_worker_and_box = self.push_box(one_loc, box, boxes)
                    if new_worker_and_box is not None:
                        move_behavior.add(one_loc)
        return move_behavior

    def get_push_behavior(self, current):
        # according to current game state, select next reachable push point and push the box
        init_worker = current.get_worker_loc()
        boxes = current.get_boxes_loc()
        one_step_reachabel = self.get_one_step_move(init_worker[0], init_worker[1])
        push_behavior = set()
        for box in boxes:
            if box in one_step_reachabel:
                new_worker_and_box = self.push_box(init_worker, box, boxes)
                if new_worker_and_box is not None:
                    push_behavior.add(new_worker_and_box)
        return push_behavior

    def expand_current_state(self, current):
        moves = self.get_move_behavior(current)
        pushes = self.get_push_behavior(current)
        successors = []
        for new_worker in moves:
            child = self.creat_game_info(current.get_boxes_loc(), new_worker, current.depth+1, current)
            successors.append(child)

        for new_worker, new_box in pushes:
            new_boxes = set(current.get_boxes_loc())
            new_boxes.remove(new_worker)
            new_boxes.add(new_box)
            child = self.creat_game_info(new_boxes, new_worker, current.depth+1, current)
            successors.append(child)
        return successors

    # def search(self, use_memory=True):
    #     pass