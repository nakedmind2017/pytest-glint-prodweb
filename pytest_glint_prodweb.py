# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest


@pytest.fixture
def sa_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import scoped_session, sessionmaker

    e = create_engine('sqlite:///:memory:')
    e.execute('PRAGMA foreign_keys=ON')
    session = scoped_session(sessionmaker(autoflush=True, autocommit=False, bind=e))

    try:
        import prodweb.database as db
        db.Session = session
    except ImportError:
        pass
    yield session

    session.remove()
    e.dispose()


@pytest.fixture
def cp_session():
    from cherrypy.lib.sessions import RamSession
    sess_mock = RamSession()
    patcher = patch('cherrypy.session', sess_mock, create=True)
    patcher.start()
    yield sess_mock
    patcher.stop()


@pytest.fixture
def cp_request(sa_session):
    patcher = patch('cherrypy.request', autospec=True)
    r = patcher.start()
    r.db = sa_session
    yield r
    patcher.stop()


@pytest.fixture
def cp_response(sa_session):
    patcher = patch('cherrypy.response', autospec=True)
    yield patcher.start()
    patcher.stop()
