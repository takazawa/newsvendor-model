from abc import ABCMeta, abstractmethod
from typing import Callable, Optional, Union

from scipy import integrate, optimize


class BaseNewsvendorModel(metaclass=ABCMeta):
    def __init__(
        self,
        retail_price: int,
        cost_price: int,
        probability_function: Callable[[float], float],
        salvaged_revenue: int = 0,
        opportunity_cost: int = 0,
    ):
        self.retail_price = retail_price
        self.cost_price = cost_price
        self.pf = probability_function
        self.salvaged_revenue = salvaged_revenue
        self.opportunity_cost = opportunity_cost
        self._max_demand: Optional[int] = None

    def critical_ratio(self) -> float:
        return (self.retail_price - self.cost_price + self.opportunity_cost) / (
            self.retail_price - self.salvaged_revenue + self.opportunity_cost
        )

    def revenue(self, quantity: float, demand: float) -> float:
        earning = self.retail_price * min(quantity, demand) + self.salvaged_revenue * max(quantity - demand, 0)
        cost = self.cost_price * quantity + self.opportunity_cost * max(demand - quantity, 0)
        return earning - cost

    @abstractmethod
    def optimal_quantity(self):
        pass

    @abstractmethod
    def expected_revenue(self, quantity: float) -> float:
        return integrate.quad(
            lambda demand: self.revenue(quantity, demand) * self.pf(demand),
            0,
            self._max_demand,
        )[0]

    def max_demand(self):
        if self._max_demand:
            return self._max_demand
        cdf: float = 0
        demand: int = 0
        while True:
            cdf += self.pf(demand)
            if cdf >= 0.99:
                break
            else:
                demand += 1
        self._max_demand = demand
        return self._max_demand


class DiscreteNewsvendorModel(BaseNewsvendorModel):
    def critical_ratio(self) -> float:
        return (self.retail_price - self.cost_price + self.opportunity_cost) / (
            self.retail_price - self.salvaged_revenue + self.opportunity_cost
        )

    def revenue(self, quantity: Union[int, float], demand: Union[int, float]) -> float:
        earning = self.retail_price * min(quantity, demand) + self.salvaged_revenue * max(quantity - demand, 0)
        cost = self.cost_price * quantity + self.opportunity_cost * max(demand - quantity, 0)
        return earning - cost

    def expected_revenue(self, quantity: int) -> float:
        revenue: float = 0
        for demand in range(0, self.max_demand()):
            p = self.pf(demand)
            revenue += self.revenue(quantity, demand) * p
            demand += 1
        return revenue

    def optimal_quantity(self):
        q: int = 0
        best_revenue: float = -float("inf")
        while True:
            revenue = self.expected_revenue(q)
            if revenue > best_revenue:
                best_revenue = revenue
            else:
                break
            q += 1
        return q - 1


class ContinuousNewsvendorModel(BaseNewsvendorModel):
    pf: Callable[[float], float]

    def __init__(
        self,
        retail_price: int,
        cost_price: int,
        probability_function: Optional[Callable[[float], float]] = None,
        inverse_cdf: Optional[Callable[[float], float]] = None,
        salvaged_revenue: int = 0,
        opportunity_cost: int = 0,
    ):
        super().__init__(
            retail_price=retail_price,
            cost_price=cost_price,
            probability_function=probability_function,
            salvaged_revenue=salvaged_revenue,
            opportunity_cost=opportunity_cost,
        )
        self.inverse_cdf: Callable[[float], float] = inverse_cdf if inverse_cdf else self._inverse_cdf

    def expected_revenue(self, quantity: float) -> float:
        return integrate.quad(
            lambda demand: self.revenue(quantity, demand) * self.pf(demand),
            0,
            self._max_demand,
        )[0]

    def optimal_quantity(self) -> float:
        return self.inverse_cdf(self.critical_ratio())

    def cdf(self, k: Union[int, float]) -> float:
        return integrate.quad(self.pf, 0, k)[0]

    def _inverse_cdf(self, quantile: float) -> float:
        sol = optimize.root_scalar(
            lambda x: self.cdf(x) - quantile,
            bracket=[0, self.max_demand()],
            method="brentq",
        )
        return sol.root
