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

# Auto-matching by common field names
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
    if not os.path.exists(file_path):
        return {}

    with open(file_path) as f:
        raw = json.load(f)

    overrides = {}
    for field, override in raw.items():
        # Simple function override: { "email": "email" }
        if isinstance(override, str):
            try:
                overrides[field] = getattr(faker, override)
            except AttributeError:
                print(f"⚠️ Warning: Faker has no method '{override}' for field '{field}'")
        # Structured override for nested fields: { "orders": { "count": 3 } }
        elif isinstance(override, dict):
            overrides[field] = override

    return overrides


def generate_field_value(field_name, field_type, custom_overrides):
    if field_name in custom_overrides:
        override = custom_overrides[field_name]
        if callable(override):
            return override()
    if field_name in FIELD_NAME_OVERRIDES:
        return FIELD_NAME_OVERRIDES[field_name]()
    return FIELD_TYPE_MAP.get(field_type, lambda: faker.word())()


def generate_doc_from_properties(properties, custom_overrides):
    doc = {}
    for field, spec in properties.items():
        field_type = spec.get("type", "text")

        if field_type in ("object", "nested") and "properties" in spec:
            nested_doc = lambda: generate_doc_from_properties(spec["properties"], custom_overrides)

            if field_type == "nested":
                count = (
                    custom_overrides.get(field, {}).get("count")
                    if isinstance(custom_overrides.get(field), dict)
                    else random.randint(1, 3)
                )
                doc[field] = [nested_doc() for _ in range(count)]
            else:
                doc[field] = nested_doc()

        else:
            doc[field] = generate_field_value(field, field_type, custom_overrides)

    return doc


def generate_doc(mapping, custom_overrides):
    properties = mapping.get("mappings", {}).get("properties", {})
    return generate_doc_from_properties(properties, custom_overrides)


def generate_docs(mapping_path, count=100, override_path="faker-overrides.json"):
    mapping = load_mapping(mapping_path)
    overrides = load_custom_overrides(override_path)
    return [generate_doc(mapping, overrides) for _ in range(count)]