"""Train/test split matching the private service rather than sklearn defaults."""

from __future__ import annotations

import random


def original_holdout_indices(
    n_rows: int,
    *,
    test_size: float = 0.2,
    random_state: int | None = 42,
) -> tuple[list[int], list[int]]:
    """Shuffle indices with ``random.Random`` and take the first floor(n*p) as test.

    This is intentionally not ``train_test_split``: the original implementation
    used Python's standard-library RNG and returned the remaining shuffled indices
    as the training order. That order also feeds the unshuffled five-fold search.
    """

    if n_rows <= 1:
        raise ValueError("At least two rows are required for a holdout split.")
    if not 0.0 < test_size < 1.0:
        raise ValueError("test_size must be in (0, 1).")
    indices = list(range(n_rows))
    rng = random.Random(random_state) if random_state is not None else random
    rng.shuffle(indices)
    test_count = max(1, int(n_rows * test_size))
    test_indices = indices[:test_count]
    train_indices = indices[test_count:]
    if not train_indices:
        raise ValueError("Holdout split left no training rows.")
    return train_indices, test_indices
