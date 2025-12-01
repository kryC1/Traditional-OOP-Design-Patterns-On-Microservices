from .providers import PaymentProvider, CreditCardProvider, PayPalProvider


class PaymentProviderFactory:
    """
    Factory Method: encapsulates creation of concrete payment providers.
    In microservices, this could map to selecting external services, configs, etc.
    """

    @staticmethod
    def create(method: str) -> PaymentProvider:
        if method == "credit_card":
            return CreditCardProvider()
        if method == "paypal":
            return PayPalProvider()
        raise ValueError(f"Unsupported payment method: {method}")
