from sqlalchemy.orm import DeclarativeBase, declared_attr


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Provides:
    - Consistent table naming
    - Shared metadata for migrations
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Automatically generate table names from class names.

        Example:
            Merchant -> merchants
            PaymentTransaction -> payment_transactions
        """
        name = cls.__name__
        # Convert CamelCase to snake_case plural
        table_name = []
        for i, char in enumerate(name):
            if char.isupper() and i != 0:
                table_name.append("_")
            table_name.append(char.lower())

        return "".join(table_name) + "s"
