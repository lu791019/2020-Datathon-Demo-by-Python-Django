import pytest

from datathon.models import get_db_connection


@pytest.fixture()
def db_conn():
    return get_db_connection()


def test_db_connection(db_conn):
    # FIXME this is no mock connection, it is REAL !

    cursor = db_conn.cursor()

    test_sql = "SELECT top 10 * from invoice_qmonster "

    cursor.execute(test_sql)

    assert len(list(cursor)) == 10
