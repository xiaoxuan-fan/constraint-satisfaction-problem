from CSPProblem import Constraint, CSPProblem
from CSPSolver import CSPSolver
from typing import List, Dict, Tuple


class CircuitBoard(object):
    def __init__(self, width: int, height: int, c: str) -> None:
        self.width = width
        self.height = height
        self.c = c
        self.domain_list: List[Tuple[int, int]] = list()

    def get_domain(self, board_width, board_height):
        for x_position in range(0, board_width - self.width + 1):
            for y_position in range(0, board_height - self.height + 1):
                self.domain_list.append((x_position, y_position))
        return self.domain_list


class CircuitConstraint(Constraint[CircuitBoard, Tuple[int, int]]):
    def __init__(self, variable_1: CircuitBoard, variable_2: CircuitBoard) -> None:
        super().__init__([variable_1, variable_2])
        self.variable_1 = variable_1
        self.variable_2 = variable_2

    def satisfied(self, assignment: Dict[CircuitBoard, Tuple[int, int]]) -> bool:
        if self.variable_1 not in assignment or self.variable_2 not in assignment:
            return True

        rec_1 = [assignment[self.variable_1][0], assignment[self.variable_1][1],
                 assignment[self.variable_1][0] + self.variable_1.width,
                 assignment[self.variable_1][1] + self.variable_1.height]
        rec_2 = [assignment[self.variable_2][0], assignment[self.variable_2][1],
                 assignment[self.variable_2][0] + self.variable_2.width,
                 assignment[self.variable_2][1] + self.variable_2.height]

        not_satisfied = max(rec_1[0], rec_2[0]) < min(rec_1[2], rec_2[2]) and max(rec_1[1], rec_2[1]) < min(rec_1[3],
                                                                                                            rec_2[3])
        return not not_satisfied


def solution_to_picture(solution: Dict[CircuitBoard, Tuple[int, int]], board_width: int, board_height: int,
                        board_char: str):
    picture = [[board_char for _ in range(board_width)] for _ in range(board_height)]
    for circuit_board, position in solution.items():
        for height in range(circuit_board.height):
            for width in range(circuit_board.width):
                picture[board_height - (position[1] + height) - 1][position[0] + width] = circuit_board.c
    for line in picture:
        print(''.join(line))
    return picture


def main():
    board_width = 10
    board_height = 3
    board_char = '.'

    # variable_info_list:List[Tuple[int,int,str]] = [(5,1,'b'),(2,1,'c'),(3,1,'a'),(5,1,'b'),(2,1,'c'),(7,1,'e'),(3,
    # 1,'a'),(2,1,'c')]
    # corrected_domain_list = [(3, 0), (8, 0), (0, 0), (3, 1), (8, 1), (0, 2), (0, 1), (8, 2)]
    variable_info_list: List[Tuple[int, int, str]] = [(5, 2, 'b'), (2, 3, 'c'), (3, 2, 'a'), (7, 1, 'e')]

    variable_list: List[CircuitBoard] = list()
    domain_list: Dict[CircuitBoard, List[int]] = dict()

    for variable_info in variable_info_list:
        circuit_board = CircuitBoard(variable_info[0], variable_info[1], variable_info[2])
        variable_list.append(circuit_board)
        domain_list[circuit_board] = circuit_board.get_domain(board_width, board_height)
    # start_index = 1
    # for i, variable in enumerate(variable_list[start_index:]):
    #     domain_list[variable] = [corrected_domain_list[i+start_index]]

    circuit_problem = CSPProblem(variable_list, domain_list)
    for i, variable_1 in enumerate(variable_list):
        for variable_2 in variable_list[i + 1:]:
            circuit_problem.add_constraints(CircuitConstraint(variable_1, variable_2))

    select_method_list = ['default', 'MRV']
    order_method_list = ['default', 'LCV']
    inference_method_list = ['default', 'AC3']
    for select_method in select_method_list:
        for order_method in order_method_list:
            for inference_method in inference_method_list:
                csp_solver = CSPSolver(circuit_problem, which_variable=select_method, inference=inference_method,
                                       which_value=order_method)
                solution = csp_solver.solve()
                solution_to_picture(solution, board_width, board_height, board_char)


if __name__ == '__main__':
    main()
