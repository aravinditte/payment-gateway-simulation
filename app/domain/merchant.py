from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class MerchantDomain:
    """
    Domain representation of a merchant.
    """
    id: UUID
    is_active: bool

    def assert_active(self) -> None:
        if not self.is_active:
            raise ValueError("Merchant is inactive")
