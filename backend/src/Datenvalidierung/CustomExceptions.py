class CounterLimitReachedError(Exception):
    """
    Exception, wenn nach *counter* Iterationen immer noch kein vernünftiges Produkt erstellt werden konnte. Wird
    auch für non_product Sachen wie das Erstellen der fiktiven Namen, oder das Erfragen einer bestimmten Uhrzeit
    oder Namen eines Employee verwendet.

    """

    def __init__(self, counter: int):
        self.message = f"Couldn't create proper product within {counter} retries"
        super().__init__(self.message)


class CreateProductTimeLimitReachedError(Exception):
    """Exception raised for products that take to lojng to be created.

    Attributes:
        product_count -- number of product which caused the error
        message -- explanation of the error
    """

    def __init__(self, message="Product could not be created within the time limit."):
        self.message = message
        super().__init__(self.message)
