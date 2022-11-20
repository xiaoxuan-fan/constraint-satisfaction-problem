from CSPProblem import Constraint, CSPProblem
from CSPSolver import CSPSolver
from typing import List, Dict


class MapColoringConstraint(Constraint[str, str]):
    def __init__(self, place_1: str, place_2: str) -> None:
        super().__init__([place_1, place_2])
        self.place_1 = place_1
        self.place_2 = place_2

    def satisfied(self, assignment: Dict[str, str]) -> bool:
        if self.place_1 not in assignment or self.place_2 not in assignment:
            return True
        return assignment[self.place_1] != assignment[self.place_2]


def main():
    variable_list: List[str] = ["Western Australia", "Northern Territory", "South Australia",
                                "Queensland", "New South Wales", "Victoria", "Tasmania"]
    domain_list: Dict[str, List[str]] = {}
    for variable in variable_list:
        domain_list[variable] = ["red", "green", "blue"]
    map_color_problem = CSPProblem(variable_list, domain_list)
    map_color_problem.add_constraints(MapColoringConstraint("Western Australia", "Northern Territory"))
    map_color_problem.add_constraints(MapColoringConstraint("Western Australia", "South Australia"))
    map_color_problem.add_constraints(MapColoringConstraint("South Australia", "Northern Territory"))
    map_color_problem.add_constraints(MapColoringConstraint("Queensland", "Northern Territory"))
    map_color_problem.add_constraints(MapColoringConstraint("Queensland", "South Australia"))
    map_color_problem.add_constraints(MapColoringConstraint("Queensland", "New South Wales"))
    map_color_problem.add_constraints(MapColoringConstraint("New South Wales", "South Australia"))
    map_color_problem.add_constraints(MapColoringConstraint("Victoria", "South Australia"))
    map_color_problem.add_constraints(MapColoringConstraint("Victoria", "New South Wales"))

    select_method_list = ['default', 'MRV']
    order_method_list = ['default', 'LCV']
    inference_method_list = ['default', 'AC3']
    for select_method in select_method_list:
        for order_method in order_method_list:
            for inference_method in inference_method_list:
                csp_solver = CSPSolver(map_color_problem, which_variable=select_method,
                                       inference=inference_method, which_value=order_method)
                solution = csp_solver.solve()
                print(solution)


if __name__ == '__main__':
    main()
