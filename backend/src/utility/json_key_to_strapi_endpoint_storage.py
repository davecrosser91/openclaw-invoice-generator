from dotenv import load_dotenv
from pydantic import BaseModel

from src.utility.strapi_endpoints import (
    STRAPI_SELLER_ENDP,
    STRAPI_INVOICE_ENDP,
    STRAPI_PRODUCT_ENDP,
    STRAPI_PDFINVOICE_ENDP,
    STRAPI_STORY_ENDP,
    STRAPI_BUYERS_ENDP,
)

load_dotenv()


class key_to_endpoint_storage(BaseModel):
    """
    Date of the last change: 02.02.2024
    Primary for Invoice_Adapter.py: split_and_prepare_dicts().
    Contains the three endpoints to separate seller, buyer and product, in the json input or dict from the invoice data
    and the remaining data such as tokens, total_cost etc.
    """

    buyer: str = STRAPI_BUYERS_ENDP
    seller: str = STRAPI_SELLER_ENDP
    products: str = STRAPI_PRODUCT_ENDP
    branche: str = STRAPI_STORY_ENDP


class invoice_keys:
    """
    Date of the last change: 02.02.2024
    Primary for Invoice_Adapter.py: split_and_prepare_dicts().
    Contains all parameters that are specific to the invoice and have nothing to do with buyer, seller, products and
    the remaining data such as tokens, total_cost etc.
    """

    dateofinvoice: str = "dateofinvoice"
    dateofdeliveryorservice: str = "dateofdeliveryorservice"
    invoicenumber: str = "invoicenumber"
    subtotal: str = "subtotal"
    taxes: str = "taxes"
    total: str = "total"


class pdf_invoice_keys:
    """
    Date of the last change: 02.02.2024
    Primary for Invoice_Adapter.py: manage_pdf_invoice_plus_relations().
    Contains all parameters of a PDFInvoice in Strapi.
    """

    pdf = "pdf"
    buyer = "buyer"
    seller = "seller"
    story = "story"
    invoice = "invoice"
    precisecontent = "precisecontent"
    template = "template"
    filled_html = "filled_html"
    comments = "comments"


class token_keys:
    """
    Date of the last change: 02.02.2024
    Primary for Invoice_Adapter.py: split_and_prepare_dicts().Contains all parameters of the remaining data such as
    tokens, total_cost etc.
    As of 02.02.2024 there is no further use of the data. It must also be checked to what extent everything is
    correct in Invoice_Generator_Class.py with regard to the calculation of tokens and costs.
    """

    product_retry_counter: str = "product_retry_counter"
    non_product_retry_counter: str = "non_product_retry_counter"
    total_prompt_tokens: str = "total_prompt_tokens"
    total_completion_tokens: str = "total_completion_tokens"
    total_cost_in_dollar: str = "total_cost_in_dollar"


class story_keys:
    """
    Date of the last change: 02.02.2024
    Primary for Invoice_Adapter.py: post_all_available_data().
    Contains all the parameters of a story in Strapi. Is used to create the story, as the stories of the products are
    still with the products. As of 02.02.2024, the industry of the seller must be requested in
    Invoice_Generator_Class.py.
    The request and Ai message is then saved in branche_user and branche_ai. Currently, "" is saved.
    """

    full_story: str = "full_story"
    productstories: str = "productstories"
    productstories_products: str = "products"
    branche: str = "branche"
    u_branche: str = "u_branche"
    ai_branche: str = "ai_branche"


class template_keys:
    """
    Date of the last change: 21.02.2024
    Primary for manage_Invoice_from_Strapi.py: get_template_from_strapi().
    Filter by products. In future also doctype and name possible.
    """

    name: str = "name"
    validated: str = "validated"
    language: str = "language"
    products: str = "products"
    doctype: str = "doctype"


class correct_product_story_keys:
    """
    Date of the last change: 02.02.2024
    Primary for Invoice_Adapter.py: fix_story_key_names().
    For the sake of simplicity, the user and AI messages (in Invoice_Generator_Class.py or in
    src/non_specific_scripts/memory_to_dict.py: create_dict_out_of_ai_and_user_lists()) are always saved with their
    number of occurrence.
    The first user message gets ..._1, the second ..._2 etc. The parameters in Strapi, however, are more specific and
    for the assignment later, the names of the variables are replaced by the names of the parameters in the tables.
    """

    user_message_1: str = "u_productname"
    ai_response_1: str = "ai_productname"
    user_message_2: str = "u_price"
    ai_response_2: str = "ai_price"
    user_message_3: str = "u_quantity"
    ai_response_3: str = "ai_quantity"
    user_message_4: str = "u_taxcontext"
    ai_response_4: str = "ai_taxcontext"


"""
Date: 08.02.2024
Dataclasses for filtering within the Strapi database. Are mainly used in manage_invoice_from_Strapi.py.
Basically, the aim is to determine the parameters that can be used for filtering, e.g. to request one or more specific
PDFs from the database. This is specifically about the PDF Invoices. The parameters buyer, seller, invoice and 
template make sense for filtering PDF invoices. Neither precisecontent, validated or story are useful filter 
parameters. Furthermore, in the 4 data classes of buyer, seller, invoice and template, only those parameters are listed
which in turn make sense/are permitted for filtering in the 4 classes. The specific explanation then follows within 
the 4 data classes. A separate data class is created for products, as it makes sense to be able to filter using the 
products when filtering with the seller, invoice and template. In turn, however, the products require a regulation on 
their part as to which parameters of the products may be checked.
"""


class PdfInvoiceKeysFilter(BaseModel):
    """
    Date of the last change: 09.02.2024
    Primary for manage_invoice_from_Strapi.py: get_existing_pdf_invoice(). Contains all parameters useful for filtering.
    All parameters of buyer, seller, invoice and template that can be used for filtering are listed.
    """

    name: str = "name"
    street: str = "street"
    email: str = "email"
    phone: str = "phone"
    fax: str = "fax"
    bankdetails: str = "bankdetails"
    employee: str = "employee"
    city: str = "city"
    postalcode: str = "postalcode"
    customerid: str = "customerid"
    ifforeigntaxidentifier: str = "ifforeigntaxidentifier"
    website: str = "website"
    taxidentifier: str = "taxidentifier"
    products: str = "products"  # Special case: is also a relation
    dateofinvoice: str = "dateofinvoice"
    dateofdeliveryorservice: str = "dateofdeliveryorservice"
    invoicenumber: str = "invoicenumber"
    subtotal: str = "subtotal"
    taxes: str = "taxes"
    total: str = "total"
    buyer: str = "buyer"  # Special case: is also a relation
    seller: str = "seller"  # Special case: is also a relation
    validated: str = "validated"
    language: str = "language"
    doctype: str = "doctype"
    quantity: str = "quantity"
    price: str = "price"
    tax: str = "tax"
    unity: str = "unity"
    taxrate: str = "taxrate"
    buyer_keys: dict = {
        "buyer": {
            name,
            street,
            email,
            phone,
            fax,
            bankdetails,
            employee,
            city,
            postalcode,
            customerid,
            ifforeigntaxidentifier,
            website,
        }
    }
    seller_keys: dict = {
        "seller": {
            name,
            street,
            email,
            phone,
            fax,
            bankdetails,
            employee,
            city,
            postalcode,
            taxidentifier,
            website,
            products,
        }
    }
    invoice_keys: dict = {
        "invoice": {
            dateofinvoice,
            dateofdeliveryorservice,
            invoicenumber,
            subtotal,
            taxes,
            total,
            products,
            buyer,
            seller,
            validated,
        }
    }
    template_keys: dict = {"template": {name, validated, language, products, doctype}}
    products_keys: dict = {"products": {name, quantity, price, tax, unity, taxrate}}

    all_keys: dict = {
        "buyer": {
            name,
            street,
            email,
            phone,
            fax,
            bankdetails,
            employee,
            city,
            postalcode,
            customerid,
            ifforeigntaxidentifier,
            website,
        },
        "seller": {
            name,
            street,
            email,
            phone,
            fax,
            bankdetails,
            employee,
            city,
            postalcode,
            taxidentifier,
            website,
            products,
        },
        "invoice": {
            dateofinvoice,
            dateofdeliveryorservice,
            invoicenumber,
            subtotal,
            taxes,
            total,
            products,
            buyer,
            seller,
            validated,
        },
        "template": {name, validated, language, products, doctype},
        "products": {name, quantity, price, tax, unity, taxrate},
    }


class HtmlPhKeys:
    """
    Date of the last change: 19.04.2024
    Primary for Invoice_Adapter -append_individual_placeholder_values()
    Names of the individual placeholders that are not product-specific.
    """

    address = "address"
    citywplc = "citywplc"
    total_transport_cost = "total_transport_cost"
    account_num = "account_num"
    contract_num = "contract_num"
    random_number = "random_number"


class HTML_PH_prods_keys:
    """
    Date of the last change: 19.04.2024
    Primary for Invoice_Adapter -append_individual_placeholder_values()
    Names of the individual placeholders that are product-specific.
    """

    product_cost = "product_cost"  # is product cost without tax to be clarified in the future
    product_cost_w_tax = "product_cost_w_tax"
    transport_cost = "transport_cost"
    position = "position"
    number = "number"


#
# @dataclass
# class buyer_keys_filter:
#     """
#     Datum der letzten Änderung: 08.02.2024
#     Primär für manage_invoice_from_Strapi.py: get_existing_pdf_invoice().
#     Enthält alle, für das Filtern mit der Buyer relation, sinnvollen Parameter.
#     Nur die relations invoice und pdf_invoice bei buyer nicht relevant.
#     Alle anderen Parameter können zur Filterung verwendet werden.
#     """
#     name: str = "name"
#     street: str = "street"
#     email: str = "email"
#     phone: str = "phone"
#     fax: str = "fax"
#     bankdetails: str = "bankdetails"
#     employee: str = "employee"
#     city: str = "city"
#     postalcode: str = "postalcode"
#     customerID: str = "customerID"
#     ifforeigntaxidentifier: str = "ifforeigntaxidentifier"
#     website: str = "website"
#     buyer = {name, street, email, phone, fax, bankdetails, employee, city, postalcode, customerID,
#              ifforeigntaxidentifier, website}
#
#
# @dataclass
# class seller_keys_filter(pdf_invoice_keys.seller):
#     """
#     Datum der letzten Änderung: 08.02.2024
#     Primär für manage_invoice_from_Strapi.py: get_existing_pdf_invoice().
#     Enthält alle, für das Filtern mit der Seller relation, sinnvollen Parameter.
#     Nur die relations invoice und pdf_invoice bei seller nicht relevant.
#     Alle anderen Parameter können zur Filterung verwendet werden.
#     """
#     name: str = "name"
#     street: str = "street"
#     email: str = "email"
#     phone: str = "phone"
#     fax: str = "fax"
#     bankdetails: str = "bankdetails"
#     employee: str = "employee"
#     city: str = "city"
#     postalcode: str = "postalcode"
#     taxidentifier: str = "taxidentifier"
#     website: str = "website"
#     products: str = "products"  # Sonderfall ist wiederum eine relation
#
#
# @dataclass
# class invoice_keys_filter:
#     """
#     Datum der letzten Änderung: 08.02.2024
#     Primär für manage_invoice_from_Strapi.py: get_existing_pdf_invoice().
#     Enthält alle, für das Filtern mit der Invoice relation, sinnvollen Parameter.
#     Nur die relations story und pdf_invoice bei invoice nicht relevant.
#     Alle anderen Parameter können zur Filterung verwendet werden.
#     """
#     dateofinvoice: str = "dateofinvoice"
#     dateofdeliveryorservice: str = "dateofdeliveryorservice"
#     invoicenumber: str = "invoicenumber"
#     subtotal: str = "subtotal"
#     taxes: str = "taxes"
#     total: str = "total"
#     products: str = "products"  # Sonderfall ist wiederum eine relation
#     buyer: str = "buyer"  # Sonderfall ist wiederum eine relation
#     seller: str = "seller"  # Sonderfall ist wiederum eine relation
#     validated: str = "validated"
#
#
# @dataclass
# class template_keys_filter:
#     """
#     Datum der letzten Änderung: 08.02.2024
#     Primär für manage_invoice_from_Strapi.py: get_existing_pdf_invoice().
#     Enthält alle, für das Filtern mit der Template relation, sinnvollen Parameter.
#     Nicht relevant sind html, description (außer es gibt mal ein einheitliches Format), entities, pdfinvoice.
#     Alle anderen Parameter können zur Filterung verwendet werden.
#     """
#     name: str = "name"
#     validated: str = "validated"
#     language: str = "language"
#     products: str = "products"
#     doctype: str = "doctype"
#
#
# @dataclass
# class products_keys_filter:
#     """
#     Datum der letzten Änderung: 08.02.2024
#     Primär für manage_invoice_from_Strapi.py: get_existing_pdf_invoice().
#     Enthält alle, für das Filtern mit der Template relation, sinnvollen Parameter.
#     Nicht relevant sind seller und invoice, da man sich dann im Kreis dreht mit der Filterung.
#     Alle anderen Parameter können zur Filterung verwendet werden.
#     """
#     name: str = "name"
#     quantity: str = "quantity"
#     price: str = "price"
#     tax: str = "tax"
#     unity: str = "unity"
#     taxrate: str = "taxrate"


"""------------------------------------------------------------------------------------------------------------------"""

# @dataclass
# class message_prefixes_to_story_names:
#     STRAPI_BUYERS_ENDP: str = "buyer"
#     STRAPI_SELLER_ENDP: str = "seller"
#     STRAPI_PRODUCT_ENDP: str = "products"
#     STRAPI_INVOICE_ENDP: str = "invoice"
#     STRAPI_STORY_ENDP: str = "story"
#

"""
Test mit Ansatz jeder Dataclass seine relations zu geben:
    Current relations:
    
    Buyer: invoice, pdfinvoice
    Invoice: buyer, seller, products, pdfinvoice
    Product: seller, invoice
    Seller: products, invoice, pdfinvoice
    
    TO BE INTEGRATED:
    Template: entities, pdfinvoice
    put_to_strapi(endpoint=STRAPI_INVOICE_ENDP, index=5, data=data, bearer_token=BEARER_TOKEN)

"""


class Buyer_dC(BaseModel):
    OWN_ENDP: str = STRAPI_BUYERS_ENDP
    STRAPI_INVOICE_ENDP: dict[str, str] = {STRAPI_INVOICE_ENDP: "invoice"}
    STRAPI_PDFINVOICE_ENDP: dict[str, str] = {STRAPI_PDFINVOICE_ENDP: "pdfinvoice"}


class Invoice_dC(BaseModel):
    OWN_ENDP: str = STRAPI_INVOICE_ENDP
    STRAPI_BUYERS_ENDP: dict[str, str] = {STRAPI_BUYERS_ENDP: "buyer"}
    STRAPI_PDFINVOICE_ENDP: dict[str, str] = {STRAPI_PDFINVOICE_ENDP: "pdfinvoice"}
    STRAPI_SELLER_ENDP: dict[str, str] = {STRAPI_SELLER_ENDP: "seller"}
    STRAPI_PRODUCT_ENDP: dict[str, str] = {STRAPI_PRODUCT_ENDP: "products"}
    STRAPI_STORY_ENDP: dict[str, str] = {STRAPI_STORY_ENDP: "story"}


class Product_dC(BaseModel):
    OWN_ENDP: str = STRAPI_PRODUCT_ENDP
    STRAPI_SELLER_ENDP: dict[str, str] = {STRAPI_SELLER_ENDP: "seller"}
    STRAPI_INVOICE_ENDP: dict[str, str] = {STRAPI_INVOICE_ENDP: "invoice"}


class Seller_dC(BaseModel):
    OWN_ENDP: str = STRAPI_SELLER_ENDP
    STRAPI_PRODUCT_ENDP: dict[str, str] = {STRAPI_PRODUCT_ENDP: "products"}
    STRAPI_INVOICE_ENDP: dict[str, str] = {STRAPI_INVOICE_ENDP: "invoice"}
    STRAPI_PDFINVOICE_ENDP: dict[str, str] = {STRAPI_PDFINVOICE_ENDP: "pdfinvoice"}


class Story_dC(BaseModel):
    OWN_ENDP: str = STRAPI_STORY_ENDP
    STRAPI_INVOICE_ENDP: dict[str, str] = {STRAPI_INVOICE_ENDP: "invoice"}
    STRAPI_PDFINVOICE_ENDP: dict[str, str] = {STRAPI_PDFINVOICE_ENDP: "pdfinvoice"}


def return_strapi_tables_as_list():
    """
    Primarily for Invoice_Adapter.py: manage_relations().
    Buyer_dC(), Invoice_dC(), Product_dC(), Seller_dC(), Story_dC() are used to set the relations that are specified in
    the tables in Strapi.
    """

    return [Buyer_dC(), Invoice_dC(), Product_dC(), Seller_dC(), Story_dC()]
