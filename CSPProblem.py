# Author: Xiaoxuan
# Date: 11/5/2022
# Problem description: constraint satisfaction problem
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Dict, List

V = TypeVar('V')  # variable type

D = TypeVar('D')  # domain type


class Constraint(Generic[V, D], ABC):
    def __init__(self, variables: List[V]) -> None:
        self.variables = variables

    @abstractmethod
    def satisfied(self, assignment: Dict[V, D]) -> bool:
        pass


class CSPProblem(object):
    def __init__(self, variables: List[V], domains: List[Constraint[V, D]]) -> None:
        self.variables = variables
        self.domains = domains
        self.constraints: Dict[V, List[Constraint[V, D]]] = dict()
        # which variables are under the influence of a certain variable
        self.influence_dict: Dict[V, List[V]] = dict()

        for variable in self.variables:
            self.constraints[variable] = []
            self.influence_dict[variable] = []

    def add_constraints(self, constraint: Constraint[V, D]):
        for variable in constraint.variables:
            self.constraints[variable].append(constraint)
            self.influence_dict[variable].extend(constraint.variables)
            self.influence_dict[variable].remove(variable)
            self.influence_dict[variable] = list(set(self.influence_dict[variable]))
