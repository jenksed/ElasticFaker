from elasticsearch import Elasticsearch, helpers
import json
from config import ES_HOST


es = Elasticsearch(ES_HOST)


def create_index(index_name, mapping_path, reset=False):
    """Create or reset index based on mapping."""
    with open(mapping_path) as f:
        mapping = json.load(f)

    if reset and es.indices.exists(index=index_name):
        print(f"⚠️ Deleting index '{index_name}'")
        es.indices.delete(index=index_name)

    if not es.indices.exists(index=index_name):
        print(f"📦 Creating index '{index_name}'")
        es.indices.create(index=index_name, body=mapping)
    else:
        print(f"✅ Index '{index_name}' already exists")


def bulk_insert(index_name, docs):
    """Bulk insert documents into the index."""
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in docs
    ]

    helpers.bulk(es, actions)
