from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):

    def __repr__(self) -> str:
        attrs = [
            f"{col}={getattr(self, col)}"
            for col in self.__table__.columns.keys()
        ]
        return f"<{self.__class__.__name__}: {", ".join(attrs)}>"
