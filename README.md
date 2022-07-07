# newsvender-model

[![test](https://github.com/takazawa/newsvendor-model/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/takazawa/newsvendor-model/actions/workflows/test.yml)

This repository is a Python implementation of the [Newsvendor Model](https://en.wikipedia.org/wiki/Newsvendor_model).

## Requirements

- `Python>=3.8`
- `scipy>=1.8.1`

## Install

```shell
pip install git+https://github.com/takazawa/newsvendor-model
```

## Model

### Newsvendor Model

#### Input (for some product)

- demand $D$ (random variable)
- retail price $p$
- purchase price $c$

#### Problem

The standard newsvendor model is to find the optimal quantity $q_{\text{opt}} $of the product, which
maximizes the expected profit $E[F(q, D)]$, where
$$
F(q, D) = p\min (q, D) - cq.
$$

The optimal solution to the problem is known to be

$$
q_{\text{opt}} = F^{-1} \left( \dfrac{p-c}{c} \right),
$$

where $F^{-1}$ is the inverse cumulative distribution function of $D$.

## Usage

The model to be imported depends on whether the probability distribution used is discrete or continuous as follows:

```python
from nvmodel import ContinuousNewsvendorModel, DiscreteNewsvendorModel
```

Using the [Wikipedia example](https://en.wikipedia.org/wiki/Newsvendor_model#Uniform_distribution),
consider the following problem:

- retail price $p = 7$
- purchase price $c = 5$
- demand $D$ follows a (continuous) uniform distribution between $D_{\min}=50$ and $D_{\max}=80$.

Then the newsvendeor model is as follows:

```python
from nvmodel import ContinuousNewsvendorModel


def p_func(x):
    d_min, d_max = 50, 80
    if d_min <= x <= d_max:
        return 1 / (d_max - d_min)
    else:
        return 0


model = ContinuousNewsvendorModel(retail_price=7,
                                  cost_price=5,
                                  probability_function=p_func)
```

Now, we can calculate values

- $\frac{p-c}{c} = $ `model.critical_ratio()`
- $q_{\text{opt}} = $ `model.optimal_quantity()`
- $F(q, D) = $ `model.revenue(q, D)`
- $E[F(q, D)] = $  `model.expected_revenue(q)`

```python
>> q_opt = model.optimal_quantity()
>> q_opt
58.57142857142857
```

### Other Samples

#### 1. Normal Distribution

```python
from scipy.stats import norm

from nvmodel import ContinuousNewsvendorModel


def normal_pdf(x):
    mu, sigma = 50, 20
    return norm(mu, sigma).pdf(x)


model = ContinuousNewsvendorModel(retail_price=7, cost_price=5, probability_function=normal_pdf)
q_opt = model.optimal_quantity()

>> q_opt
39.04454355287975
```

In the Continuous Model, the inverse CDF is computed approximately.
It can also be computed exactly by explicitly giving inverseCDF as follows.

```python
from scipy.stats import norm

from nvmodel import ContinuousNewsvendorModel


def normal_inverse_cdf(x):
    mu, sigma = 50, 20
    return mu + sigma * norm.ppf(x)


model = ContinuousNewsvendorModel(retail_price=7,
                                  cost_price=5,
                                  inverse_cdf=normal_inverse_cdf)
q_opt = model.optimal_quantity()

>> q_opt
38.68102356134274
```

#### 2. Poisson Distribution

- retail price $p = 8$
- purchase price $c = 5$
- demand $D$ follows the poisson distribution (mean=25)
- salvaged revenue $s = 4$
    - a profit per unit from unsold products

```python
from scipy.stats import poisson

from nvmodel import DiscreteNewsvendorModel


def poisson_pmf(x):
    return poisson.pmf(x, 25)


model = DiscreteNewsvendorModel(retail_price=8,
                                cost_price=5,
                                probability_function=poisson_pmf,
                                salvaged_revenue=4)
q_opt = model.optimal_quantity()

>> q_opt
28
```


