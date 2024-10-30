import os
import sys

import numpy as np

# Add the root folder to the system paths so python can resolve the project imports
# TODO: Add src folder to path

src_path = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path.insert(0, src_path)
from necost import generate_monte_carlo_samples


def test_generate_monte_carlo_samples__sampling_level(input_params_data):
    constant_params = {
        "params_data": input_params_data,
        "discount_rate": 3
    }

    samples_1 = generate_monte_carlo_samples(sampling_amount=10_000, **constant_params)
    samples_2 = generate_monte_carlo_samples(sampling_amount=50_000, **constant_params)
    samples_3 = generate_monte_carlo_samples(sampling_amount=0, **constant_params)
    samples_4 = generate_monte_carlo_samples(sampling_amount=34_721, **constant_params)
    samples_5 = generate_monte_carlo_samples(sampling_amount=12, **constant_params)

    assert len(samples_1) == 10_000
    assert len(samples_2) == 50_000
    assert len(samples_3) == 0
    assert len(samples_4) == 34_721
    assert len(samples_5) == 12


def test_generate_monte_carlo_samples__column_names_match_input(input_params_data):
    samples = generate_monte_carlo_samples(
        sampling_amount=100,
        params_data=input_params_data,
        discount_rate=3
    )

    assert len(samples.columns) == len(input_params_data.columns)
    assert (samples.columns == input_params_data.columns).all()


def test_generate_monte_carlo_samples__seeded(input_params_data):
    constant_params = {
        "sampling_amount": 100,
        "params_data": input_params_data,
        "discount_rate": 3
    }

    # Chose 100 random seeds between 0 and 10,000, then check that calling the sampler
    # two different times with the same seed generates the same values.
    for seed in np.random.randint(0, 10_000, 100):
        samples_seed_1 = generate_monte_carlo_samples(seed=seed, **constant_params)
        samples_seed_2 = generate_monte_carlo_samples(seed=seed, **constant_params)
        assert (samples_seed_1.values == samples_seed_2.values).all()
