from evaluation import precision_at_k


def test_precision_at_k():
    retrieved_ids = ["a", "b", "c"]
    relevant_ids = {"a", "c"}

    assert precision_at_k(
        retrieved_ids,
        relevant_ids,
        3,
    ) == 2 / 3


def test_precision_at_k_with_no_relevant_results():
    retrieved_ids = ["a", "b", "c"]
    relevant_ids = {"x"}

    assert precision_at_k(
        retrieved_ids,
        relevant_ids,
        3,
    ) == 0.0


def test_precision_at_k_with_empty_results():
    assert precision_at_k(
        [],
        {"a"},
        3,
    ) == 0.0