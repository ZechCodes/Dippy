from __future__ import annotations
from ast import literal_eval
from dippy.labels.storage import StorageInterface, NOT_SET, Label
from dippy.sqlalchemy_connector import SQLAlchemyConnector
from sqlalchemy import Column, Integer, String
from typing import Any, Optional


class LabelModel(SQLAlchemyConnector.BaseModel):
    __tablename__ = "dippy_labels"

    id = Column(Integer, primary_key=True)
    object_id = Column(Integer, nullable=False)
    object_type = Column(String(32), nullable=False)
    key = Column(String(256), nullable=False)
    value = Column(String(2048), nullable=False)


class SQLAlchemyStorage(StorageInterface):
    db: SQLAlchemyConnector

    async def delete(self, object_type: str, object_id: int, key: str):
        with self.db.session() as session:
            session.query(LabelModel).filter(
                (LabelModel.object_id == object_id)
                & (LabelModel.object_type == object_type)
                & (LabelModel.key == key)
            ).delete()
            session.commit()

    async def find(
        self,
        object_type: Optional[str] = None,
        object_id: Optional[int] = None,
        *,
        key: Optional[str] = None,
        value: Any = NOT_SET,
    ) -> list[Label]:
        with self.db.session() as session:
            query = session.query(LabelModel)
            if object_type:
                query = query.filter(LabelModel.object_type == object_type)
            if object_id:
                query = query.filter(LabelModel.object_id == object_id)
            if key:
                query = query.filter(LabelModel.key == key)

            return [
                Label(row.object_type, row.object_id, row.key, literal_eval(row.value))
                for row in query.all()
                if value is NOT_SET or literal_eval(row.value) == value
            ]

    async def get(
        self, object_type: str, object_id: int, key: str, default: Any = None
    ) -> Any:
        result = self._get(object_type, object_id, key)
        return literal_eval(result.value) if result else default

    async def has(self, object_type: str, object_id: int, key: str) -> bool:
        with self.db.session() as session:
            count = (
                session.query(LabelModel)
                .filter(
                    (LabelModel.object_type == object_type)
                    & (LabelModel.object_id == object_id)
                    & (LabelModel.key == key)
                )
                .count()
            )
            return count > 0

    async def set(self, object_type: str, object_id: int, key: str, value: Any):
        label = self._get(object_type, object_id, key)
        with self.db.session() as session:
            if label:
                label.value = repr(value)
                session.add(label)
            else:
                label = LabelModel(
                    object_type=object_type,
                    object_id=object_id,
                    key=key,
                    value=repr(value),
                )
            session.add(label)
            session.commit()

    async def setup(self):
        return

    def _get(self, object_type: str, object_id: int, key: str) -> LabelModel:
        with self.db.session() as session:
            result: LabelModel = (
                session.query(LabelModel)
                .filter(
                    (LabelModel.object_type == object_type)
                    & (LabelModel.object_id == object_id)
                    & (LabelModel.key == key)
                )
                .first()
            )
            return result
