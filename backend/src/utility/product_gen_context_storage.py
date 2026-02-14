def return_context_assignment() -> dict:
    """
    Returns the key of the context thats to be used when asking a specific question. The assignments are used to:
    1. Make sure only relevant information is given in the context.
    2. to save tokens (speeds up the generation and saves money)
    :return: dict with the assignements
    """
    return assignment_dict


assignment_dict = {
    "q1_product": ["q0_branch"],
    "q2_price": ["q1_product"],
    "q3_quantity": ["q1_product"],
    "q4_VAT_0": ["q0_branch", "q1_product"],
    "q5_VAT_7": ["q0_branch", "q1_product"],
}
