from datetime import datetime
from sqlalchemy import Integer, func
from sqlalchemy.orm import Mapped, mapped_column, declared_attr


class BaseModel:
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )
