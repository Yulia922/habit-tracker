from sqlalchemy import Engine, create_engine


def get_engine(url: str = "sqlite:///habits.db") -> Engine:
    return create_engine(url)
