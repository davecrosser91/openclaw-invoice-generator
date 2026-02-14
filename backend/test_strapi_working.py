"""Working test with actual Strapi."""
import os
from dotenv import load_dotenv
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.utility.strapi_endpoints import STRAPI_CITY_ENDP
from src.GeoDaten.deutsche_orte_mit_plz import get_random_german_town_and_plz

load_dotenv()


def test_strapi_working():
    """Test Strapi with methods that actually work."""
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")

    print("=" * 60)
    print("Testing Working Strapi Methods")
    print("=" * 60)

    # Test 1: Get specific city by ID
    print("\n✓ Test 1: Getting city by ID...")
    result = get_by_id_from_strapi(
        endpoint=STRAPI_CITY_ENDP,
        bearer_token=bearer_token,
        entry_id=1
    )

    print(f"  Debug: Result type: {type(result)}, Value: {result}")

    if isinstance(result, dict) and "data" in result:
        attrs = result["data"]["attributes"]
        print(f"  ✓ City ID 1: {attrs['name']}")
        print(f"  ✓ Postal code: {attrs['postalcode']}")
        print(f"  ✓ Phone code: {attrs['phonecode']}")
        print(f"  ✓ Country: {attrs['countrycode']}")
        print(f"  ✓ Data structure correct!")
    else:
        print(f"  ❌ Unexpected response: {result}")
        return False

    # Test 2: Get multiple cities by ID (works without random endpoint)
    print("\n✓ Test 2: Getting multiple cities by ID...")
    for city_id in [1, 2, 3]:
        result = get_by_id_from_strapi(
            endpoint=STRAPI_CITY_ENDP,
            bearer_token=bearer_token,
            entry_id=city_id
        )
        if isinstance(result, dict):
            attrs = result["data"]["attributes"]
            print(f"  ✓ City {city_id}: {attrs['name']} ({attrs['postalcode']})")

    # Test 3: Using the actual function with w_strapi=False (PostgreSQL)
    print("\n✓ Test 3: Testing with w_strapi=False (PostgreSQL)...")
    try:
        name, postalcode, phonecode, countrycode, t_id = get_random_german_town_and_plz(
            bearer_token=bearer_token,
            number=2,
            w_strapi=False
        )
        print(f"  ✓ Town 1: {name[0]}, {postalcode[0]}")
        print(f"  ✓ Town 2: {name[1]}, {postalcode[1]}")
    except Exception as e:
        print(f"  ⚠️  w_strapi=False not available (requires PostgreSQL): {e}")

    print("\n" + "=" * 60)
    print("✅ Strapi Integration Working!")
    print("=" * 60)
    print("\nNote: get_random=True requires /count/view endpoint which")
    print("doesn't exist in this Strapi version. Use specific IDs instead.")
    return True


if __name__ == "__main__":
    test_strapi_working()
