from pysmt.shortcuts import *
from solver.solver_basic import SokobanSolverBasic

class SymbolArray:
    def __init__(self, name, shape):
        self.name = name
        self.dim = 1 if type(shape) == int else len(shape)
        self.arr = {}
        self.reverse_mapping = {}

    def __getitem__(self, idx):
        if type(idx) == int:
            idx = (idx,)
        assert len(idx) == self.dim
        if idx not in self.arr:
            self.arr[idx] = Symbol(self.get_symbol_name(idx))
        self.reverse_mapping[self.arr[idx]] = (self.name, idx)
        return self.arr[idx]

    def get_symbol_name(self, idx):
        return self.name + "(" + ",".join(map(lambda x: str(x), idx)) + ")"

    def get_used_keys(self):
        return set(self.reverse_mapping.keys())

    def get_values(self, symb):
        return self.reverse_mapping[symb]


class SokobanSolverSAT(SokobanSolverBasic):
    def __init__(self, map, step_limit):
        super().__init__(map)
        self.nx = max(len(row) for row in map)
        self.ny = len(map)
        self.step_limit = step_limit
        self.move = SymbolArray("m", shape=(self.nx, self.ny, self.nx, self.ny, self.step_limit))
        self.push = SymbolArray("p", shape=(self.nx, self.ny, self.nx, self.ny, self.step_limit))
        self.worker_at = SymbolArray("w", shape=(self.nx, self.ny, self.step_limit+1))
        self.box_at = SymbolArray("b", shape=(self.nx, self.ny, self.step_limit+1))
        self.goal_time_step = [self.step_limit]
        self.init_solver()

    def init_solver(self):
        self.formula = self.encode_constraints()
        self.solver = Solver()
        self.solver.add_assertion(self.formula)

    def get_used_keys(self):
        keys = set()
        for arr_keys in [self.move, self.push, self.worker_at, self.box_at]:
            keys = keys.union(arr_keys.get_used_keys())
        return keys

    def encode_constraints(self):
        all_cons = [self.encode_init_state, self.encode_goal_state, self.encode_action_schema, self.encode_state_schema]  #
        all_f = []
        for func in all_cons:
            partial_fomula = func()
            all_f.append(partial_fomula)
        final_formula = And(all_f)
        return final_formula

    def encode_init_state(self):
        all_f = []
        for i,j in self.playabel:
            if (i,j) == self.init_worker_loc:
                all_f.append(self.worker_at[i,j,0])
            else:
                all_f.append(Not(self.worker_at[i,j,0]))
            if (i,j) in self.init_boxes_loc:
                all_f.append(self.box_at[i,j,0])
            else:
                all_f.append(Not(self.box_at[i,j,0]))
        return And(all_f)

    def encode_goal_state(self):
        all_f = []
        for time in self.goal_time_step:
            all_right_box = []
            for i, j in self.docks:
                all_right_box.append(self.box_at[i, j, time])
            all_f.append(And(all_right_box))
        return Or(all_f)

    def get_action_schema(self, action, para):
        assert len(para) == 5
        init_loc_x, init_loc_y, offset_x, offset_y, time_step = para
        if action is self.move:
            pre = And(self.worker_at[init_loc_x, init_loc_y, time_step],
                      Not(self.box_at[init_loc_x + offset_x, init_loc_y + offset_y, time_step]))
            add = self.worker_at[init_loc_x + offset_x, init_loc_y + offset_y, time_step+1]
            dele = Not(self.worker_at[init_loc_x, init_loc_y, time_step+1])
        elif action is self.push:
            pre = And(self.worker_at[init_loc_x, init_loc_y, time_step],
                      self.box_at[init_loc_x + offset_x, init_loc_y + offset_y, time_step],
                      Not(self.box_at[init_loc_x + 2*offset_x, init_loc_y + 2*offset_y, time_step]),
                      FALSE() if (init_loc_x + 2*offset_x, init_loc_y + 2*offset_y) in self.walls else TRUE())
            add = And(self.worker_at[init_loc_x + offset_x, init_loc_y + offset_y, time_step+1],
                      self.box_at[init_loc_x + 2*offset_x, init_loc_y + 2*offset_y, time_step+1])
            dele = And(Not(self.worker_at[init_loc_x, init_loc_y, time_step+1]),
                       Not(self.box_at[init_loc_x + offset_x, init_loc_y + offset_y, time_step+1]))
        else:
            raise NotImplementedError("Action not defined")
        return pre, add, dele

    def encode_action_schema(self):
        all_f = []
        for time_step_action in range(self.step_limit):
            for i,j in self.playabel:
                reachable = self.get_one_step_move(i, j)
                for tar_i, tar_j in reachable:
                    offset_x, offset_y = tar_i - i, tar_j - j
                    action = self.move[i, j, tar_i, tar_j, time_step_action]
                    pre, add, dele = self.get_action_schema(self.move, (i, j, offset_x, offset_y, time_step_action))
                    all_f.append(Implies(action, pre))
                    all_f.append(Implies(action, add))
                    all_f.append(Implies(action, dele))

                    action = self.push[i, j, tar_i, tar_j, time_step_action]
                    pre, add, dele = self.get_action_schema(self.push, (i, j, offset_x, offset_y, time_step_action))
                    all_f.append(Implies(action, pre))
                    all_f.append(Implies(action, add))
                    all_f.append(Implies(action, dele))


        return And(all_f)

    def encode_state_schema(self):
        all_f = []
        for time_step_action in range(self.step_limit):
            for i,j in self.playabel:
                reachable = self.get_one_step_move(i, j)
                possible_out_move = []
                possible_in_move = []
                for tar_i, tar_j in reachable:
                    possible_out_move.append(self.move[i, j, tar_i, tar_j, time_step_action])
                    possible_in_move.append(self.move[tar_i, tar_j, i, j, time_step_action])
                    possible_out_move.append(self.push[i, j, tar_i, tar_j, time_step_action])
                    possible_in_move.append(self.push[tar_i, tar_j, i, j, time_step_action])
                all_f.append(Implies(And(Not(self.worker_at[i, j, time_step_action]), self.worker_at[i, j, time_step_action+1]),
                                         ExactlyOne(possible_in_move)))
                all_f.append(Implies(And(self.worker_at[i, j, time_step_action], Not(self.worker_at[i, j, time_step_action+1])),
                                         ExactlyOne(possible_out_move)))

                possible_out_push = []
                possible_in_push = []
                for tar_i, tar_j in reachable:
                    offset_x, offset_y = tar_i - i, tar_j - j
                    if (tar_i + offset_x, tar_j + offset_y) not in self.walls:
                        possible_in_push.append(self.push[tar_i + offset_x, tar_j + offset_y, tar_i, tar_j, time_step_action])
                    if (i - offset_x, j - offset_y) not in self.walls:
                        possible_out_push.append(self.push[i - offset_x, j - offset_y, i, j, time_step_action])
                all_f.append(Implies(And(Not(self.box_at[i, j, time_step_action]), self.box_at[i, j, time_step_action+1]),
                                         ExactlyOne(possible_in_push)))
                all_f.append(Implies(And(self.box_at[i, j, time_step_action], Not(self.box_at[i, j, time_step_action+1])),
                                         ExactlyOne(possible_out_push)))
        return And(all_f)

    def solve_for_one(self):
        controls = None
        if self.solver.solve():
            controls = self.parse_solution()
            print(f"Use {len(controls)} steps")
            print(controls)
            # partial_model = [EqualsOrIff(k, self.solver.get_value(k)) for k in self.get_used_keys()]
            # self.solver.add_assertion(Not(And(partial_model)))
        else:
            print(f"No solution found in {self.step_limit} steps")
        return controls

    def parse_solution(self):
        ### get a sequence of worker positions ###
        worker = [self.worker_at.get_values(k) for k in self.worker_at.get_used_keys() if self.solver.get_value(k).is_true()]
        worker = sorted(worker, key=lambda t: t[1][2])
        controls = []
        pre_x, pre_y = self.init_worker_loc
        for pos in worker:
            _, (x, y, _) = pos
            offset_x, offset_y = x - pre_x, y - pre_y
            if offset_x != 0 or offset_y != 0:
                controls.append(self.control_mapping[(offset_x, offset_y)])
                pre_x = x
                pre_y = y
        return controls




