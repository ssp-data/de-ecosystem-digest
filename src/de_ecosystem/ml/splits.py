import xorq.api as xo


def make_splits(
    feature_matrix: object,
    test_size: float = 0.2,
    random_seed: int = 42,
) -> tuple[object, object]:
    """
    Split feature matrix into train/test using xorq's deterministic splitter.
    Returns (train_expr, test_expr).
    """
    df = feature_matrix.execute()
    n = len(df)
    train, test = xo.train_test_splits(
        xo.memtable(df),
        unique_key="tool",
        test_sizes=test_size,
        num_buckets=max(n, 10),
        random_seed=random_seed,
    )
    return train, test
