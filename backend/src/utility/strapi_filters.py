from dataclasses import dataclass

"""------------------------------------------------------------------------------------------------------------------"""
"""Strapi Filters: Filters that are used for filtering for specific parameters in Strapi"""
"""The idea is to build a dataclass to hide the abbreviations behind the operations that are easier to understand and 
   only need to know the operation you want to do.
   Comparison: https://docs.strapi.io/dev-docs/api/rest/filters-locale-publication#filtering for the abbreviations
   Example for filtering: Search for the templates with at least 2 products:
   Postman:
   http://localhost:1337/api/templates?filters[products][$gte]=2
   ------------------------------------------------------------
   Python: (src.Requests.Request_Strapi : get_by_id_from_strapi())
   parameter = "products"
   greater_or_equal = Strapi_filters.greater_or_equal
   endpoint = api/templates?filters[parameter][greater_or_equal]=2
   bearer_token = BEARER_TOKEN
   entry_id = None (ergibt, dass ganze Tabelle durchsucht wird)
   get_by_id_from_strapi(endpoint=endpoint, bearer_token=BEARER_TOKEN, entry_id=None)
"""
"""------------------------------------------------------------------------------------------------------------------"""


@dataclass
class Strapi_filters:
    equal: str = "$eq"  # Equal
    equal_c_i: str = "$eqi"  # Equal (case-insensitive)
    not_equal: str = "$ne"  # Not equal
    not_equal_c_i: str = "$nei"  # Not equal (case-insensitive)
    less: str = "$lt"  # Less than
    less_or_equal: str = "$lt"  # Less than or equal to
    greater: str = "$gt"  # Greater than
    greater_or_equal: str = "$gte"  # Greater than or equal to
    in_array: str = "$in"  # Included in an array
    not_in_array: str = "$notIn"  # Not included in an array
    contains: str = "$contains"  # Contains
    contains_not: str = "$notContains	"  # Does not contain
    contains_c_i: str = "$containsi"  # Contains (case-insensitive)
    contains_not_c_i: str = "$notContainsi"  # Does not contain (case-insensitive)
    null: str = "$null"  # Is null
    not_null: str = "$notNull"  # Is not null
    between: str = "$between"  # Is between
    start_with: str = "$startsWith"  # Starts with
    start_with_c_i: str = "$startsWithi"  # Starts with (case-insensitive)
    ends_with: str = "$endsWith"  # Ends with
    ends_with_c_i: str = "$endsWithi"  # Ends with (case-insensitive)
    or_strapi: str = "$or"  # Joins the filters in an "or" expression
    and_strapi: str = "$and"  # Joins the filters in an "and" expression
    not_strapi: str = "$not"  # Joins the filters in an "not" expression
