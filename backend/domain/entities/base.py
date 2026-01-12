"""Base entity class for domain entities."""

from datetime import datetime, timezone
from uuid import UUID, uuid4


class BaseEntity:
    def __init__(
        self,
        id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ):
        self._id = id or uuid4()
        self._created_at = created_at or datetime.now(timezone.utc)
        self._updated_at = updated_at or datetime.now(timezone.utc)

    @property
    def id(self) -> UUID:
        """Entity unique identifier."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Entity creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Entity last update timestamp."""
        return self._updated_at

    def _update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self._updated_at = datetime.now(timezone.utc)

    def __eq__(self, other: object) -> bool:
        """Two entities are equal if they have the same ID."""
        if not isinstance(other, BaseEntity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Hash based on entity ID."""
        return hash(self.id)

    def __repr__(self) -> str:
        """String representation of the entity."""
        return f"{self.__class__.__name__}(id={self.id})"
