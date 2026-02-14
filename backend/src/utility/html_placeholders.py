"""------------------------------------------------------------------------------------------------------------------"""

from src.types import JSON

"""HTML Placeholders: Placeholders that are to be replaced by the equivalents of the json output"""
"""Gedanke ist, dass die gleichen "keys" verwendet werden, um das dictionary durchzugehen, und zu überprüfen ob value des 
   HTML_Placeholders[key] in der html vorhanden ist, und wenn ja soll {value} mit dem entsprechenden value des gleichen 
   keys aus der jsonoutput[key] ersetzt werden.
   TL DR:
   template_html_als_str = get_Template_aus_DB
   if placeholder = HTML_Placeholders[special_key] is in template_html_als_str
        replacement = JSONOutput[special_key] (alle Invoice Daten)
   --> template_html_als_str.replace(placeholder,replacement)  
   
   Gedanke 2(besser): 
   1.) Zuerst wird sich template geholt. template_html_als_str = get_Template_aus_DB
   2.) Es wird überprüft, welche Placeholder in diesem speziellen Template vorhanden sind. 
   3.) Es werden nur diese speziellen Inhalte aus der Datenbank entnommen (geht das so?)
   
   
   """

"""------------------------------------------------------------------------------------------------------------------"""
"""keys heissen (bis auf derzeit: adresse und citywplc, die separat erstellt werden) wie die Parameter in Strapi
   Die Übereinstimmung des Namens ist essentiell für das Mapping von Inhalt in Strapi mit dem Namen und dem zugeordneten
   value in HTML_Placeholders für die keys."""
HTMLPlaceholders: JSON = {
    "buyer": {
        "address": "{buyer_address}",
        "street": "{buyer_street}",
        "city": "{buyer_city}",
        "citywplc": "{buyer_citywplc}",
        "name": "{buyer_name}",
        "employee": "{buyer_employee}",
        "email": "{buyer_email}",
        "website": "{buyer_website}",
        "phone": "{buyer_phone}",
        "fax": "{buyer_fax}",
        "iban": "{buyer_iban}",
        "bic": "{buyer_bic}",
        "ifforeigntaxidentifier": "{buyer_ifforeigntaxidentifier}",
        "customerid": "{buyer_customerid}",
        "account_num": "{buyer_account_number}",
    },
    "seller": {
        "address": "{seller_address}",
        "street": "{seller_street}",
        "city": "{seller_city}",
        "citywplc": "{seller_citywplc}",
        "name": "{seller_name}",
        "employee": "{seller_employee}",
        "email": "{seller_email}",
        "website": "{seller_website}",
        "phone": "{seller_phone}",
        "fax": "{seller_fax}",
        "iban": "{seller_iban}",
        "bic": "{seller_bic}",
        "taxidentifier": "{seller_taxidentifier}",
    },
    "dateofinvoice": "{dateofinvoice}",
    "dateofdeliveryorservice": "{dateofdeliveryorservice}",
    "invoicenumber": "{invoicenumber}",
    "products": {
        "name": "{product_name_}",
        "price": "{product_price_}",
        "unity": "{product_unity_}",
        "quantity": "{product_quantity_}",
        "taxrate": "{product_sales_tax_percent_}",
        "tax": "{product_sales_tax_cost_}",
        "product_cost": "{product_cost_wo_tax_}",
        "product_cost_w_tax": "{product_cost_w_tax_}",
        "transport_cost": "{product_transport_cost_}",
        "position": "{product_pos_}",
        "number": "{product_num_}",
    },
    "subtotal": "{subtotal}",
    "taxes": "{taxes}",
    "total": "{total}",
    "total_transport_cost": "{total_transport_cost}",
    "contract_num": "{contract_number}",
}

SpecialHTMLPlaceholders: list[JSON] = [
    {"address": "{buyer_address}"},
    {"citywplc": "{buyer_citywplc}"},
    {"address": "{seller_address}"},
    {"citywplc": "{seller_citywplc}"},
    {"total_transport_cost": "{total_transport_cost}"},
    {"account_num": "{buyer_account_number}"},
    {"contract_num": "{contract_number}"},
]
SpecialHTMLPlaceholders_Prods: list[JSON] = [
    {"product_cost": "{product_cost_wo_tax_}"},
    {"product_cost_w_tax": "{product_cost_w_tax_}"},
    {"transport_cost": "{product_transport_cost_}"},
    {"position": "{product_pos_}"},
    {"number": "{product_num_}"},
]
