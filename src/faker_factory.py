import json
from faker import Faker
import random
import os

faker = Faker()

# Default ES type → faker generators
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

# Auto-overrides based on common field names
FIELD_NAME_OVERRIDES = {
    "email": lambda: faker.email(),
    "username": lambda: faker.user_name(),
    "first_name": lambda: faker.first_name(),
    "last_name": lambda: faker.last_name(),
    "bio": lambda: faker.text(),
    "street": lambda: faker.street_address(),
    "city": lambda: faker.city(),
    "postal_code": lambda: faker.postcode(),
    "zipcode": lambda: faker.postcode(),
    "country": lambda: faker.country(),
    "phone": lambda: faker.phone_number(),
    "ip": lambda: faker.ipv4(),
    "created_at": lambda: faker.date_time_this_decade().isoformat()
}


def load_mapping(mapping_path):
    with open(mapping_path) as f:
        return json.load(f)


def load_custom_overrides(file_path="faker-overrides.json"):
    """
    Load user-defined field overrides from a JSON file.
    Example:
        {
            "email": "email",
            "created_at": "date_time_this_century"
        }
    """
    if not os.path.exists(file_path):
        return {}

    with open(file_path) as f:
        raw = json.load(f)

    overrides = {}
    for field, faker_func_name in raw.items():
        try:
            faker_func = getattr(faker, faker_func_name)
            overrides[field] = faker_func
        except AttributeError:
            print(f"⚠️ Warning: Faker has no method '{faker_func_name}' for field '{field}'")

    return overrides


def generate_field_value(field_name, field_type, custom_overrides):
    """Choose faker function based on (1) custom overrides, (2) name match, (3) type match."""
    if field_name in custom_overrides:
        return custom_overrides[field_name]()
    if field_name in FIELD_NAME_OVERRIDES:
        return FIELD_NAME_OVERRIDES[field_name]()
    return FIELD_TYPE_MAP.get(field_type, lambda: faker.word())()


def generate_doc_from_properties(properties, custom_overrides):
    """Recursively generate a document from a field -> type map."""
    doc = {}
    for field, spec in properties.items():
        if spec.get("type") == "object" and "properties" in spec:
            doc[field] = generate_doc_from_properties(spec["properties"], custom_overrides)
        else:
            field_type = spec.get("type", "text")
            doc[field] = generate_field_value(field, field_type, custom_overrides)
    return doc


def generate_doc(mapping, custom_overrides):
    properties = mapping.get("mappings", {}).get("properties", {})
    return generate_doc_from_properties(properties, custom_overrides)


def generate_docs(mapping_path, count=100, override_path="faker-overrides.json"):
    mapping = load_mapping(mapping_path)
    overrides = load_custom_overrides(override_path)
    return [generate_doc(mapping, overrides) for _ in range(count)]