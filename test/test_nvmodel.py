from scipy.stats import norm, poisson

from nvmodel import ContinuousNewsvendorModel, DiscreteNewsvendorModel

"""
This test is based on samples from wikipedia(https://en.wikipedia.org/wiki/Newsvendor_model).
"""


def uniform_inverse_cdf(x: float, d_min: float = 50, d_max: float = 80) -> float:
    return d_min + (d_max - d_min) * x


def uniform_p_function(x: float, d_min: float = 50, d_max: float = 80) -> float:
    if d_min <= x <= d_max:
        return 1 / (d_max - d_min)
    else:
        return 0


def normal_inverse_cdf(x: float, mu: float = 50, sigma=20) -> float:
    return mu + sigma * norm.ppf(x)


def normal_pdf(x: float, mu: float = 50, sigma=20) -> float:
    return norm(mu, sigma).pdf(x)


def test_wiki_sample_uniform_with_inverse_cdf():
    """
    Given inverse cdf, calculate optimal quantity
    """
    model = ContinuousNewsvendorModel(retail_price=7, cost_price=5, inverse_cdf=uniform_inverse_cdf)
    q_opt = model.optimal_quantity()
    assert abs(q_opt - 59) < 1


def test_wiki_sample_uniform_with_p_function():
    """
    Given pdf, calculate optimal quantity
    """
    model = ContinuousNewsvendorModel(retail_price=7, cost_price=5, probability_function=uniform_p_function)
    q_opt = model.optimal_quantity()
    assert abs(q_opt - 59) < 1


def test_wiki_sample_normal_dist_with_inverse_cdf():
    model = ContinuousNewsvendorModel(retail_price=7, cost_price=5, inverse_cdf=normal_inverse_cdf)
    q_opt = model.optimal_quantity()
    assert abs(q_opt - 39) < 1


def test_wiki_sample_normal_dist_with_p_function():
    model = ContinuousNewsvendorModel(retail_price=7, cost_price=5, probability_function=normal_pdf)
    q_opt = model.optimal_quantity()
    assert abs(q_opt - 39) < 1


def poisson_pmf(x, mu=25):
    return poisson.pmf(x, mu)


def test_poisson_sample():
    model = DiscreteNewsvendorModel(retail_price=8, cost_price=5, probability_function=poisson_pmf, salvaged_revenue=4)
    q_opt = model.optimal_quantity()
    assert q_opt == 28
