import argparse
import json
from elastic_client import create_index, bulk_insert
from faker_factory import generate_docs



def interactive_mode(mapping_path, count):
    print(f"🧪 Generating {count} fake documents from {mapping_path}...\n")
    docs = generate_docs(mapping_path, count)

    for i, doc in enumerate(docs):
        print(f"[Doc {i+1}] {json.dumps(doc, indent=2)}")

    print("\n📦 Preview complete.")

    save = input("💾 Do you want to save the generated documents to a file? (y/n): ").strip().lower()
    if save == 'y':
        file_path = input("Enter filename (e.g., output.json): ").strip()
        with open(file_path, 'w') as f:
            json.dump(docs, f, indent=2)
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

    args = parser.parse_args()

    if args.interactive:
        interactive_mode(args.mapping, args.count)
        return

    if not args.index:
        print("❌ --index is required when not in interactive mode.")
        return

    docs = generate_docs(args.mapping, args.count)
    create_index(args.index, args.mapping, reset=args.reset)
    bulk_insert(args.index, docs)

    print(f"✅ Inserted {len(docs)} documents into '{args.index}'")


if __name__ == "__main__":
    main()
