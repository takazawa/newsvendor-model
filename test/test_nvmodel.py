import random

from scipy.stats import norm

from nvmodel import NewsvendorModel


def uniform_inverse_cdf(x: float, d_min: float = 50, d_max: float = 80) -> float:
    return d_min + (d_max - d_min) * x


def normal_inverse_cdf(x: float, mu: float = 50, sigma=20):
    return mu + sigma * norm.ppf(x)


def uniform_p_function(x: float) -> float:
    d_min = 50
    d_max = 80
    if d_min <= x <= d_max:
        return 1 / (d_max - d_min)


def test_wiki_sample_uniform():
    model = NewsvendorModel(
        retail_price=7, cost_price=5, inverse_cdf=uniform_inverse_cdf)
    q_opt = model.optimal_quantity()
    assert abs(q_opt - 59) < 1


def test_wiki_sample_normal_dist():
    model = NewsvendorModel(retail_price=7, cost_price=5, inverse_cdf=normal_inverse_cdf)
    q_opt = model.optimal_quantity()
    assert abs(q_opt - 39) < 1
