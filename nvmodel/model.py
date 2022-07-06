from typing import Callable, Union, Optional

from scipy import integrate
from scipy import optimize


class DiscreteNewsvendorModel:

    def __init__(self,
                 retail_price: int,
                 cost_price: int,
                 probability_function: Callable[[float], float],
                 salvaged_revenue: int = 0,
                 opportunity_cost: int = 0):
        self.retail_price = retail_price
        self.cost_price = cost_price
        self.pf = probability_function
        self.salvaged_revenue = salvaged_revenue
        self.opportunity_cost = opportunity_cost
        self.max_demand: Optional[float] = None

    def critical_ratio(self) -> float:
        return (self.retail_price - self.cost_price + self.opportunity_cost) / (
                self.retail_price - self.salvaged_revenue + self.opportunity_cost
        )

    def revenue(self, quantity: Union[int, float], demand: Union[int, float]) -> float:
        earning = self.retail_price * min(quantity, demand) + self.salvaged_revenue * max(quantity - demand, 0)
        cost = self.cost_price * quantity + self.opportunity_cost * max(demand - quantity, 0)
        return earning - cost

    def expected_revenue(self, quantity: int) -> float:
        cdf: float = 0
        demand: int = 0
        revenue: float = 0
        while True:
            if 1 - cdf <= 0.001:
                break
            p = self.pf(demand)
            revenue += self.revenue(quantity, demand) * p
            cdf += p
            demand += 1
        return revenue

    def optimal_quantity(self):
        q: int = 0
        best_revenue: float = - float("inf")
        while True:
            revenue = self.expected_revenue(q)
            if revenue > best_revenue:
                best_revenue = revenue
            else:
                break
            q += 1
        return best_revenue


class NewsvendorModel:

    def __init__(self,
                 retail_price: int,
                 cost_price: int,
                 probability_function: Optional[Callable[[float], float]] = None,
                 cdf: Optional[Callable[[float], float]] = None,
                 inverse_cdf: Optional[Callable[[float], float]] = None,
                 is_discrete: bool = True,
                 salvaged_revenue: int = 0,
                 opportunity_cost: int = 0):
        self.retail_price = retail_price
        self.cost_price = cost_price
        self.pf = probability_function
        self.cdf = cdf if cdf else self._cdf
        self.inverse_cdf: Callable[[float], float] = inverse_cdf if inverse_cdf else self._inverse_cdf
        self.is_discrete = is_discrete
        self.salvaged_revenue = salvaged_revenue
        self.opportunity_cost = opportunity_cost
        self.max_demand: Optional[float] = None

    def critical_ratio(self) -> float:
        return (self.retail_price - self.cost_price + self.opportunity_cost) / (
                self.retail_price - self.salvaged_revenue + self.opportunity_cost
        )

    def revenue(self, quantity: float, demand: float) -> float:
        earning = self.retail_price * min(quantity, demand) + self.salvaged_revenue * max(quantity - demand, 0)
        cost = self.cost_price * quantity + self.opportunity_cost * max(demand - quantity, 0)
        return earning - cost

    def expected_revenue(self, quantity: float, min_demand=0, max_demand=1000) -> float:
        return self._continuous_expected_revenue(quantity, min_demand, max_demand)

    def _continuous_expected_revenue(self, quantity: float, min_demand: float, max_demand: float) -> float:
        return integrate.quad(lambda demand: self.revenue(quantity, demand) * self.pf(demand), min_demand, max_demand)

    def optimal_quantity(self) -> float:
        return self.inverse_cdf(self.critical_ratio())

    def _cdf(self, k: Union[int, float]) -> float:
        return integrate.quad(self.pf, 0, k)

    def _inverse_cdf(self, quantile: float):
        sol = optimize.root_scalar(lambda x: self.cdf(x) - quantile, bracket=[0, 100], method='brentq')
        return sol.root
