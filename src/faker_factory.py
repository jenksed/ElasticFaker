import json
from faker import Faker
import random

faker = Faker()

# Simple type mapping from ES → Faker
FIELD_TYPE_MAP = {
    "keyword": lambda: faker.word(),
    "text": lambda: faker.sentence(),
    "date": lambda: faker.iso8601(),
    "integer": lambda: random.randint(18, 99),
    "long": lambda: random.randint(1000, 100000),
    "float": lambda: round(random.uniform(1, 1000), 2),
    "boolean": lambda: random.choice([True, False]),
    "ip": lambda: faker.ipv4(),
    "email": lambda: faker.email()
}


def load_mapping(mapping_path):
    with open(mapping_path) as f:
        return json.load(f)


def generate_doc(mapping):
    """Generate a single document based on mapping."""
    props = mapping.get("mappings", {}).get("properties", {})
    doc = {}
    for field, field_info in props.items():
        field_type = field_info.get("type", "text")
        generator = FIELD_TYPE_MAP.get(field_type, lambda: faker.word())
        doc[field] = generator()
    return doc


def generate_docs(mapping_path, count=100):
    """Generate a list of fake documents."""
    mapping = load_mapping(mapping_path)
    return [generate_doc(mapping) for _ in range(count)]
