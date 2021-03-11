from pytest import fixture
from dippy.sqlalchemy_connector import SQLAlchemyConnector
import sqlalchemy


@fixture
def db():
    return SQLAlchemyConnector("sqlite+pysqlite://")


@fixture
def table():
    class TestTable(SQLAlchemyConnector.BaseModel):
        __tablename__ = "test_table"

        id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
        message = sqlalchemy.Column(sqlalchemy.Text, nullable=False)

    return TestTable


def test_connector(db, table):
    db.create_tables()
    with db.session() as session:
        row = table(message="Hello World")
        session.add(row)
        session.commit()

    with db.session() as session:
        row = session.query(table).filter(table.message == "Hello World").first()
        assert row.message == "Hello World"
