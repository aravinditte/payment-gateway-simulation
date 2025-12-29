"""Repository pattern for database operations."""

from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(ABC, Generic[T]):
    """Base repository for CRUD operations."""

    def __init__(self, session: AsyncSession, model_class: type[T]) -> None:
        """Initialize repository.

        Args:
            session: SQLAlchemy async session
            model_class: Model class for this repository
        """
        self.session = session
        self.model_class = model_class

    async def create(self, **kwargs: Any) -> T:
        """Create and save entity.

        Args:
            **kwargs: Entity attributes

        Returns:
            T: Created entity
        """
        entity = self.model_class(**kwargs)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, entity_id: str) -> Optional[T]:
        """Get entity by ID.

        Args:
            entity_id: Entity ID

        Returns:
            Optional[T]: Entity or None
        """
        return await self.session.get(self.model_class, entity_id)

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Get all entities with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            list[T]: List of entities
        """
        stmt = select(self.model_class).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, entity: T, **kwargs: Any) -> T:
        """Update entity attributes.

        Args:
            entity: Entity to update
            **kwargs: Attributes to update

        Returns:
            T: Updated entity
        """
        for key, value in kwargs.items():
            setattr(entity, key, value)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def delete(self, entity: T) -> None:
        """Delete entity.

        Args:
            entity: Entity to delete
        """
        await self.session.delete(entity)
        await self.session.flush()

    async def commit(self) -> None:
        """Commit transaction."""
        await self.session.commit()

    async def rollback(self) -> None:
        """Rollback transaction."""
        await self.session.rollback()
