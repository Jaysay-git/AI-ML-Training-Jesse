from vector_store import collection


results = collection.get(
    include=["documents", "metadatas"]
)

paragraph_count = 0
fixed_count = 0

for metadata in results["metadatas"]:
    if metadata["chunking_strategy"] == "paragraph":
        paragraph_count += 1
    elif metadata["chunking_strategy"] == "fixed":
        fixed_count += 1

print(f"Total stored chunks: {len(results['documents'])}")
print(f"Paragraph chunks: {paragraph_count}")
print(f"Fixed-size chunks: {fixed_count}")
