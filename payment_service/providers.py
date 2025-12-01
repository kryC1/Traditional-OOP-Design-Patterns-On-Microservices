from abc import ABC, abstractmethod


class PaymentProvider(ABC):
    @abstractmethod
    def charge(self, user_id: str, amount: float) -> bool:
        """Return True if payment succeeded."""
        raise NotImplementedError


class CreditCardProvider(PaymentProvider):
    def charge(self, user_id: str, amount: float) -> bool:
        print(f"[CreditCard] Charging user={user_id}, amount={amount}")
        return True  # pretend always succeeds


class PayPalProvider(PaymentProvider):
    def charge(self, user_id: str, amount: float) -> bool:
        print(f"[PayPal] Charging user={user_id}, amount={amount}")
        return True
