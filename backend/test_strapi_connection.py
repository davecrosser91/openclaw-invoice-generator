"""Quick test to verify Strapi connection works."""
import os
from dotenv import load_dotenv
from src.Requests.Request_strapi import get_by_id_from_strapi
from src.utility.strapi_endpoints import STRAPI_CITY_ENDP
from src.GeoDaten.deutsche_orte_mit_plz import get_random_german_town_and_plz

load_dotenv()


def test_strapi_connection():
    """Test basic Strapi connection."""
    bearer_token = os.getenv("STRAPI_BEARER_TOKEN")
    strapi_url = os.getenv("STRAPI_URL")

    if not bearer_token:
        print("❌ STRAPI_BEARER_TOKEN not set in .env")
        return False

    if not strapi_url:
        print("❌ STRAPI_URL not set in .env")
        return False

    print(f"✓ STRAPI_URL: {strapi_url}")
    print(f"✓ Bearer token configured: {bearer_token[:20]}...")

    try:
        # Test getting all cities first (simpler request)
        print("\n🧪 Testing get_by_id_from_strapi with STRAPI_CITY_ENDP (get all)...")
        result = get_by_id_from_strapi(
            endpoint=STRAPI_CITY_ENDP,
            bearer_token=bearer_token,
            get_random=False,
            entry_id=0
        )

        print(f"Response type: {type(result)}")
        print(f"Response preview: {str(result)[:200]}...")

        if isinstance(result, dict) and "data" in result:
            city_data = result["data"]
            print(f"✓ Successfully fetched city: {city_data.get('attributes', {}).get('name', 'Unknown')}")
            print(f"  Response structure looks correct: {list(city_data.keys())}")

            # Test the actual function we're using
            print("\n🧪 Testing get_random_german_town_and_plz...")
            name, postalcode, phonecode, countrycode, t_id = get_random_german_town_and_plz(
                bearer_token=bearer_token,
                number=1,
                w_strapi=True
            )
            print(f"✓ Successfully fetched town data:")
            print(f"  Name: {name}")
            print(f"  Postal code: {postalcode}")
            print(f"  Phone code: {phonecode}")
            print(f"  Country code: {countrycode}")
            print(f"  ID: {t_id}")

            return True
        else:
            print(f"❌ Unexpected response structure: {result}")
            return False

    except Exception as e:
        print(f"❌ Error connecting to Strapi: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Strapi Connection")
    print("=" * 60)

    success = test_strapi_connection()

    print("\n" + "=" * 60)
    if success:
        print("✅ All Strapi integration tests passed!")
    else:
        print("❌ Strapi integration tests failed")
    print("=" * 60)
