# Author: Xiaoxuan
# Date: 11/10/2022
# Problem solution: backtracking search
from copy import deepcopy
from typing import Dict, List
from CSPProblem import D, V, CSPProblem
import time


class CSPSolver(object):
    def __init__(self, problem: CSPProblem, inference='default', which_variable='default',
                 which_value='default') -> None:
        self.csp_problem = deepcopy(problem)
        self.assignment: Dict[V, D] = dict()

        self._which_variable = which_variable
        self._which_value = which_value
        self._inference = inference

        self.call_count = 0

    def backtracking_search(self, curr_assignment=None):
        if curr_assignment is None:
            curr_assignment = {}
        self.call_count += 1
        if len(curr_assignment) == len(self.csp_problem.variables):
            return curr_assignment
        assignment = None
        next_variable: V = self._choose_next_variable(curr_assignment)
        domain_list = self._choose_domain_order(next_variable, assignment)
        for value in domain_list:
            temp_assignment = curr_assignment.copy()
            temp_assignment[next_variable] = value
            if self._check_consistent(next_variable, temp_assignment):
                previous_domain = self._update_domain(next_variable, value)

                inference_result = self._run_inference(temp_assignment)
                if inference_result is not None:
                    temp_assignment = self._add_inference(inference_result, temp_assignment)
                    assignment = self.backtracking_search(temp_assignment)
                    if assignment is not None:
                        return assignment

                self.csp_problem.domains = previous_domain
        return None

    def solve(self):
        self.call_count = 0
        start_time = time.time()
        solution = self.backtracking_search()
        end_time = time.time()
        print(
            "select method: {} , order method: {}, inference method: {}".format(self._which_variable, self._which_value,
                                                                                self._inference))
        print(
            "The solve takes {:.2f} seconds with {} times of backtrack".format(end_time - start_time, self.call_count))

        if solution is None:
            print('No Solution Found')
        else:
            return solution

    def _remove_assignment(self, tested_variable, value, current_domain):
        self.csp_problem.domains[tested_variable] = current_domain
        for variable in self.csp_problem.influence_dict[tested_variable]:
            self.csp_problem.domains[variable].append(value)

    def _update_domain(self, tested_variable, value):
        current_domain = dict()
        for k, v in self.csp_problem.domains.items():
            current_domain[k] = deepcopy(v)
        self.csp_problem.domains[tested_variable] = [value]
        for variable in self.csp_problem.influence_dict[tested_variable]:
            if value in self.csp_problem.domains[variable]:
                self.csp_problem.domains[variable].remove(value)
        return current_domain

    def _add_inference(self, inference_result: Dict[V, D], temp_assignment: Dict[V, D]) -> Dict[V, D]:
        for variable, value in inference_result.items():
            temp_assignment[variable] = value
            self._update_domain(variable, value)
        return temp_assignment

    def _check_consistent(self, variable: V, assignment: Dict[V, D]):
        for constraint in self.csp_problem.constraints[variable]:
            if not constraint.satisfied(assignment):
                return False
        return True

    # choose the next variable to be assigned a value according to different heuristics
    def _choose_next_variable(self, assignments: Dict[V, D]) -> V:
        unassigned_variable_list: List[V] = [v for v in self.csp_problem.variables if v not in assignments]
        if self._which_variable == "MRV":
            return self._minimum_remaining_value(assignments, unassigned_variable_list)
        else:
            return unassigned_variable_list[0]

    def _choose_domain_order(self, variable: V, assignment: Dict[V, D]) -> List[D]:
        if self._which_value == 'LCV':
            return self._least_constraining_value(variable, assignment)
        else:
            return self.csp_problem.domains[variable]

    def _minimum_remaining_value(self, assignments: Dict[V, D], unassigned_variable_list: List[V]) -> V:
        remaining_value_count: Dict[V, int] = dict()
        for variable in unassigned_variable_list:
            remaining_value_count[variable] = len(self.csp_problem.domains[variable])
        # a list of (variable, remaining value count), in ascending order of remaining value count
        sorted_variable_list = sorted(remaining_value_count.items(), key=lambda x: x[1], reverse=False)
        # a list of variable(s) with the same number of remaining values
        tie_list = list()
        for item in sorted_variable_list:
            if item[1] == sorted_variable_list[0][1]:
                tie_list.append(item[0])
            else:
                break
        if len(tie_list) == 1:
            return sorted_variable_list[0][0]
        else:
            return self._degree_heuristic(assignments, tie_list)

    def _degree_heuristic(self, assignments: Dict[V, D], tie_list: List[V]) -> V:
        remaining_constraint_count: Dict[V, int] = dict()
        for variable in tie_list:
            remaining_constraint_count[variable] = 0
            influenced_variables = self.csp_problem.influence_dict[variable]
            for influenced_variable in influenced_variables:
                if influenced_variable not in assignments:
                    remaining_constraint_count[variable] += 1

        # a list of (variable, remaining constraint count), in descending order of remaining constraint count
        sorted_constraint_list = sorted(remaining_constraint_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_constraint_list[0][0]

    def _least_constraining_value(self, current_variable: V, assignment: Dict[V, D]) -> List[D]:
        influenced_count_dict: Dict[D, int] = dict()

        for value in self.csp_problem.domains[current_variable]:
            influenced_count_dict[value] = 0
            for variable in self.csp_problem.influence_dict[current_variable]:
                if assignment is not None and variable in assignment:
                    continue
                if value in self.csp_problem.domains[variable]:
                    influenced_count_dict[value] += 1
        influenced_count_dict = sorted(influenced_count_dict.items(), key=lambda x: x[1])
        domain_order_list = [item[0] for item in influenced_count_dict]
        return domain_order_list

    def _run_inference(self, assignment: Dict[V, D]) -> Dict[V, D]:
        if self._inference == 'AC3':
            return self._AC3(assignment)
        else:
            return {}

    def _AC3(self, assignment: Dict[V, D]) -> Dict[V, D]:

        unassigned_variable_list = [v for v in self.csp_problem.variables if v not in assignment]
        inference_result = dict()
        queue = list()

        for variable_1 in self.csp_problem.variables:
            for variable_2 in self.csp_problem.influence_dict[variable_1]:
                queue.append((variable_1, variable_2))
                # queue.append((variable_2, variable_1))

        while queue:
            variable_1, variable_2 = queue.pop(0)
            if self._remove_inconsistent_values(variable_1, variable_2):
                if len(self.csp_problem.domains[variable_1]) == 0:
                    return None
                for variable in self.csp_problem.influence_dict[variable_1]:
                    queue.append((variable, variable_1))

        for variable in unassigned_variable_list:
            if len(self.csp_problem.domains[variable]) == 1:
                inference_result[variable] = self.csp_problem.domains[variable][0]

        return inference_result

    def _remove_inconsistent_values(self, variable_1: V, variable_2: V) -> bool:
        removed = False
        for value_1 in self.csp_problem.domains[variable_1]:
            value_keep = False
            for value_2 in self.csp_problem.domains[variable_2]:
                check_assignment = {variable_1: value_1, variable_2: value_2}
                for constraint in self.csp_problem.constraints[variable_1]:
                    if variable_2 in constraint.variables and constraint.satisfied(check_assignment):
                        value_keep = True
            if not value_keep:
                self.csp_problem.domains[variable_1].remove(value_1)
                removed = True
        return removed
