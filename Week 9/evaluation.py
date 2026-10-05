from retrieval import hybrid_search


EVALUATION_SET = [
    {
        "question": "What department and position does the employee have?",
        "relevant_ids": {
            "Jesse Osifade - (Q2).pdf-paragraph-0",
            "Jesse Osifade - (Q2).pdf-fixed-0",
        },
    },
    {
        "question": "What were the employee's most important achievements?",
        "relevant_ids": {
            "Jesse Osifade - (Q2).pdf-paragraph-1",
            "Jesse Osifade - (Q2).pdf-fixed-2",
        },
    },
    {
        "question": "What are the employee's most important aims and tasks in the next quarter?",
        "relevant_ids": {
            "Jesse Osifade - (Q2).pdf-paragraph-2",
            "Jesse Osifade - (Q2).pdf-fixed-5",
        },
    },
    {
        "question": "What training or experiences would benefit the employee in the next quarter?",
        "relevant_ids": {
            "Jesse Osifade - (Q2).pdf-paragraph-2",
            "Jesse Osifade - (Q2).pdf-fixed-6",
        },
    },
]


def precision_at_k(
    retrieved_ids: list[str],
    relevant_ids: set[str],
    k: int,
) -> float:
    """Calculate precision@k."""
    top_k = retrieved_ids[:k]

    if not top_k:
        return 0.0

    relevant_retrieved = sum(
        1
        for source_id in top_k
        if source_id in relevant_ids
    )

    return relevant_retrieved / len(top_k)


def evaluate(k: int = 3) -> list[dict]:
    """Evaluate hybrid retrieval on the labelled questions."""
    results = []

    for item in EVALUATION_SET:
        retrieved = hybrid_search(
            item["question"],
            n_results=k,
        )

        retrieved_ids = [
            result["id"]
            for result in retrieved
        ]

        precision = precision_at_k(
            retrieved_ids,
            item["relevant_ids"],
            k,
        )

        results.append(
            {
                "question": item["question"],
                "retrieved_ids": retrieved_ids,
                "precision_at_k": precision,
            }
        )

    return results


if __name__ == "__main__":
    results = evaluate(k=3)

    total_precision = 0.0

    for result in results:
        print("\nQuestion:")
        print(result["question"])

        print("Retrieved:")
        for source_id in result["retrieved_ids"]:
            print(f"  - {source_id}")

        print(
            f"Precision@3: "
            f"{result['precision_at_k']:.2f}"
        )

        total_precision += result["precision_at_k"]

    average_precision = (
        total_precision / len(results)
    )

    print(
        f"\nAverage Precision@3: "
        f"{average_precision:.2f}"
    )