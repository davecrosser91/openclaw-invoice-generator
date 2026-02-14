# Filter für Strapi: Gebaut mit, https://docs.strapi.io/dev-docs/api/rest/interactive-query-builder"""
# Bsp: Name und URL von PDF (STRAPI_ONLY_URL_AND_NAME_OF_PDF_FILTER)
#   Endpoint: http://localhost:1337/api/pdf-invoices/36
# {
#  populate: {
#    pdf: {
#      fields: ['url','name']
#    }
#  },
#  fields: ["id"]
# }
# Ergebnis: http://localhost:1337/api/pdf-invoices/36?populate[pdf][fields][0]=url&populate[pdf][fields][1]=name&fields[0]=id

STRAPI_ONLY_IDS_FILTER = "?fields[0]=id"
STRAPI_ONLY_URL_OF_PDF_FILTER = "?populate[pdf][fields][0]=url&fields[0]=id"
STRAPI_URL_AND_NAME_OF_PDF_FILTER = (
    "?populate[pdf][fields][0]=url&populate[pdf][fields][1]=name&fields[0]=id"
)
STRAPI_URL_AND_NAME_OF_PDF_AND_NAME_OF_TEMPLATE_FILTER = "?populate[pdf][fields][0]=url&populate[pdf][fields][1]=name&populate[template][fields][0]=name&fields[0]=id"
STRAPI_URL_OF_PDF_AND_NAME_OF_TEMPLATE_FILTER = (
    "?populate[pdf][fields][0]=url&populate[template][fields][0]=name&fields[0]=id"
)
STRAPI_GET_ALL_COMPANY_NAMES_FILTER = "?pagination[page]=0&pagination[pageSize]=100&fields[0]=name"  # iterate through pages from metadata (17-04-2024 591 compoanies -> 6 pages)
STRAPI_GET_ALL_INVOICE_PRODUCTNAMES_FILTER = "?populate[products][fields][0]=name"
