"""Test Pydantic class attribute access."""
from src.utility.json_key_to_strapi_endpoint_storage import key_to_endpoint_storage

# Test hasattr and getattr on the Pydantic class
keys_to_test = ["buyer", "seller", "products", "branche"]

print("Testing hasattr and getattr on key_to_endpoint_storage class:")
for key in keys_to_test:
    has_attr = hasattr(key_to_endpoint_storage, key)
    print(f"  hasattr(key_to_endpoint_storage, '{key}'): {has_attr}")
    if has_attr:
        value = getattr(key_to_endpoint_storage, key)
        print(f"    getattr value: {value}")
        print(f"    type: {type(value)}")

# Try with an instance
print("\nTrying with an instance:")
instance = key_to_endpoint_storage()
for key in keys_to_test:
    has_attr = hasattr(instance, key)
    print(f"  hasattr(instance, '{key}'): {has_attr}")
    if has_attr:
        value = getattr(instance, key)
        print(f"    getattr value: {value}")
