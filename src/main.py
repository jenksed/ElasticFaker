import argparse
import json
import csv
from elastic_client import create_index, bulk_insert
from faker_factory import generate_docs


def flatten_dict(d, parent_key='', sep='.'):
    """
    Flatten nested dictionaries for CSV output.
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Store arrays as JSON strings for CSV
            items.append((new_key, json.dumps(v, default=str)))
        else:
            items.append((new_key, v))
    return dict(items)


def interactive_mode(mapping_path, count, override_path, format):
    print(f"🧪 Generating {count} fake documents from {mapping_path}...\n")
    docs = generate_docs(mapping_path, count, override_path)

    for i, doc in enumerate(docs):
        print(f"[Doc {i+1}] {json.dumps(doc, indent=2, default=str)}")

    print("\n📦 Preview complete.")

    save = input("💾 Do you want to save the generated documents to a file? (y/n): ").strip().lower()
    if save == 'y':
        file_path = input("Enter filename (e.g., output.json or output.csv): ").strip()
        
        if format == "csv" or file_path.endswith(".csv"):
            flat_docs = [flatten_dict(doc) for doc in docs]
            fieldnames = sorted(set().union(*(d.keys() for d in flat_docs)))
            with open(file_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flat_docs)
        else:
            with open(file_path, 'w') as f:
                json.dump(docs, f, indent=2, default=str)

        print(f"✅ Saved to {file_path}")
    else:
        print("❌ Skipping file save.")


def main():
    parser = argparse.ArgumentParser(description="Generate fake data into Elasticsearch.")
    parser.add_argument("--index", help="Target index name")
    parser.add_argument("--mapping", required=True, help="Path to mapping file")
    parser.add_argument("--count", type=int, default=100, help="Number of documents to generate")
    parser.add_argument("--reset", action="store_true", help="Delete and recreate index")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode: preview data and optionally export")
    parser.add_argument("--faker-overrides", default="faker-overrides.json", help="Path to faker override config file")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Export format for saved preview output (json or csv)")

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.mapping, args.count, args.faker_overrides, args.format)
        return

    if not args.index:
        print("❌ --index is required when not in interactive mode.")
        return

    docs = generate_docs(args.mapping, args.count, args.faker_overrides)
    create_index(args.index, args.mapping, reset=args.reset)
    bulk_insert(args.index, docs)

    print(f"✅ Inserted {len(docs)} documents into '{args.index}'")


if __name__ == "__main__":
    main()