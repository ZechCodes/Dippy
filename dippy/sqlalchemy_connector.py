from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import sqlalchemy.orm


class SQLAlchemyConnector:
    BaseModel = declarative_base()

    def __init__(self, connection):
        self._connection = sqlalchemy.create_engine(connection)
        self._session_maker = sqlalchemy.orm.sessionmaker(bind=self._connection)

    def create_tables(self):
        self.BaseModel.metadata.create_all(self._connection)

    def session(self):
        return SQLAlchemySession(self._session_maker())


class SQLAlchemySession:
    def __init__(self, session):
        self._session = session

    def __enter__(self):
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self._session.rollback()
        return False
