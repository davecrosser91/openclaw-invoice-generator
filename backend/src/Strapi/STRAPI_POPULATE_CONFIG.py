"""Generated with the help of the STRAPI query builder: https://docs.strapi.io/dev-docs/api/rest/interactive-query-builder.
   The remaining table entries are output as they are not relations, but direct entries.
   Example output is then:
   json_file = get_by_id_from_strapi(endpoint=endpoint_for_all_invoice_data, bearer_token=BEARER_TOKEN, entry_id=71)
   json_file
Out[20]:
{'data': [{'id': 71,
   'attributes': {'invoicenumber': '23-0323882',
    'dateofinvoice': '2023-03-22T06:20:00.000Z',
    'subtotal': 275000,
    'taxes': 52250,
    'total': 327250,
    'validated': False,
    'dateofdeliveryorservice': '2022-06-28T00:31:31.000Z',
    'createdAt': '2024-01-29T16:32:27.310Z',
    'updatedAt': '2024-01-30T14:41:01.202Z',
    'publishedAt': '2024-01-29T16:32:27.308Z',
    'products': {'data': [{'id': 143,
       'attributes': {'name': 'Smart Automation System',
        'quantity': 25,
        'taxrate': '19%',
        'price': 1000,
        'tax': 4750,
        'unity': 'Stück'}},
      {'id': 144,
       'attributes': {'name': 'Schunk Ceramic 3DP',
        'quantity': 5,
        'taxrate': '19%',
        'price': 50000,
        'tax': 47500,
        'unity': 'Set'}}]},
    'buyer': {'data': {'id': 84,
      'attributes': {'name': 'Tönnies Holding ApS & Co. KG',
       'street': 'Alter-Sparkassen-Steig 1',
       'email': 'info@tönnies-holding-aps-&-co.-kg.de',
       'phone': '7651 217',
       'fax': '7651 913181',
       'bankdetails': 'DE49 0291 4309 3405 0',
       'employee': 'Ivan Bußmann',
       'postalcode': '79877',
       'city': 'Friedenweiler',
       'customerid': 'CID93822',
       'ifforeigntaxidentifier': ''}}},
    'seller': {'data': {'id': 80,
      'attributes': {'name': ' Schunk Innovations',
       'street': 'Markgrafenheider Straße 97',
       'email': 'info@-schunk-innovations.de',
       'phone': '4352 7800',
       'fax': '4352 2292',
       'bankdetails': None,
       'employee': None,
       'postalcode': '24351',
       'city': 'Damp',
       'taxidentifier': 'DE84027050407'}}},
    'story': {'data': {'id': 10, 'attributes': {}}}}}],
 'meta': {'pagination': {'page': 1,
   'pageSize': 25,
   'pageCount': 1,
   'total': 1}}}

"""


def populate_all_invoice_data(invoice_id: int = None):
    """
    URL to retrieve the information of all invoices or one specific invoice.
    :param invoice_id: ID that specifies which invoice is involved.
    :return: All information on either all invoices, if ID = None, or a specific invoice,
             if ID != None, that are stored in Strapi.
    """
    if invoice_id is None:
        return (
            "api/invoices?populate[products]"
            "[fields][0]=name&populate[products]"
            "[fields][1]=quantity&populate[products]"
            "[fields][2]=taxrate&populate[products]"
            "[fields][3]=price&populate[products]"
            "[fields][4]=tax&populate[products]"
            "[fields][5]=unity&populate[buyer]"
            "[fields][0]=name&populate[buyer]"
            "[fields][1]=street&populate[buyer]"
            "[fields][2]=email&populate[buyer]"
            "[fields][3]=phone&populate[buyer]"
            "[fields][4]=fax&populate[buyer]"
            "[fields][5]=iban&populate[buyer]"
            "[fields][6]=bic&populate[buyer]"
            "[fields][7]=employee&populate[buyer]"
            "[fields][8]=postalcode&populate[buyer]"
            "[fields][9]=city&populate[buyer]"
            "[fields][10]=customerid&populate[buyer]"
            "[fields][11]=ifforeigntaxidentifier&populate[buyer]"
            "[fields][12]=website&populate[seller]"
            "[fields][0]=name&populate[seller]"
            "[fields][1]=street&populate[seller][fields]"
            "[2]=email&populate[seller]"
            "[fields][3]=phone&populate[seller]"
            "[fields][4]=fax&populate[seller]"
            "[fields][5]=iban&populate[seller]"
            "[fields][6]=bic&populate[seller]"
            "[fields][7]=employee&populate[seller]"
            "[fields][8]=postalcode&populate[seller]"
            "[fields][9]=city&populate[seller]"
            "[fields][10]=taxidentifier&populate[seller]"
            "[fields][11]=website&populate[story][fields][0]=id"
        )
    else:
        return (
            f"/api/invoices/{invoice_id}?populate[products]"
            "[fields][0]=name&populate[products]"
            "[fields][1]=quantity&populate[products]"
            "[fields][2]=taxrate&populate[products]"
            "[fields][3]=price&populate[products]"
            "[fields][4]=tax&populate[products]"
            "[fields][5]=unity&populate[buyer]"
            "[fields][0]=name&populate[buyer]"
            "[fields][1]=street&populate[buyer]"
            "[fields][2]=email&populate[buyer]"
            "[fields][3]=phone&populate[buyer]"
            "[fields][4]=fax&populate[buyer]"
            "[fields][5]=iban&populate[buyer]"
            "[fields][6]=bic&populate[buyer]"
            "[fields][7]=employee&populate[buyer]"
            "[fields][8]=postalcode&populate[buyer]"
            "[fields][9]=city&populate[buyer]"
            "[fields][10]=customerid&populate[buyer]"
            "[fields][11]=ifforeigntaxidentifier&populate[buyer]"
            "[fields][12]=website&populate[seller]"
            "[fields][0]=name&populate[seller]"
            "[fields][1]=street&populate[seller][fields]"
            "[2]=email&populate[seller]"
            "[fields][3]=phone&populate[seller]"
            "[fields][4]=fax&populate[seller]"
            "[fields][5]=iban&populate[seller]"
            "[fields][6]=bic&populate[seller]"
            "[fields][7]=employee&populate[seller]"
            "[fields][8]=postalcode&populate[seller]"
            "[fields][9]=city&populate[seller]"
            "[fields][10]=taxidentifier&populate[seller]"
            "[fields][11]=website&populate[story][fields][0]=id"
        )


"""For use on the website to get return from endpoint_for_all_invoice_data on further change"""
# {
#   populate: {
#     products: {
#       fields: ['name', 'quantity', 'taxrate', 'price', 'tax', 'unity']
#     },
#     buyer: {
#       fields: ['name', 'street', 'email', 'phone', 'fax',
#                'bankdetails','employee','postalcode','city',
#                'customerid','ifforeigntaxidentifier','website']
#     },
#     seller: {
#       fields: ['name', 'street', 'email', 'phone', 'fax', 'bankdetails',
#                'employee','postalcode','city','taxidentifier','website']
#     },
#     story: {
#       fields: ['id']
#     },
#   },
# }


# BU
# return (f"/api/invoices?populate[products][fields][0]=name&populate[products]"
#         "[fields][1]=quantity&populate[products][fields][2]=taxrate&populate[products]"
#         "[fields][3]=price&populate[products][fields][4]=tax&populate[products]"
#         "[fields][5]=unity&populate[buyer][fields][0]=name&populate[buyer][fields][1]=street&populate[buyer]"
#         "[fields][2]=email&populate[buyer][fields][3]=phone&populate[buyer][fields][4]=fax&populate[buyer]"
#         "[fields][5]=bankdetails&populate[buyer][fields][6]=employee&populate[buyer]"
#         "[fields][7]=postalcode&populate[buyer][fields][8]=city&populate[buyer]"
#         "[fields][9]=customerid&populate[buyer][fields][10]=ifforeigntaxidentifier&populate[buyer]"
#         "[fields][11]=website&populate[seller][fields][0]=name&populate[seller]"
#         "[fields][1]=street&populate[seller][fields][2]=email&populate[seller]"
#         "[fields][3]=phone&populate[seller][fields][4]=fax&populate[seller]"
#         "[fields][5]=bankdetails&populate[seller][fields][6]=employee&populate[seller]"
#         "[fields][7]=postalcode&populate[seller][fields][8]=city&populate[seller]"
#         "[fields][9]=taxidentifier&populate[seller][fields][10]=website&populate[story][fields][0]=id")
