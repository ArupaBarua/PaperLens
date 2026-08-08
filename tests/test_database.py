from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.database import Base
from backend.database.models import (
    ChatSession,
    ChatMessage,
    Paper,
    Figure,
)
from backend.database import crud
from backend.schemas.figure import FigureInfo


# ---------------------------------------------------------
# Test database setup
# ---------------------------------------------------------

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={
        "check_same_thread": False
    }
)

TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def setup_database():
    """
    Creates all database tables.
    """

    Base.metadata.create_all(
        bind=engine
    )


def teardown_database():
    """
    Removes all database tables.
    """

    Base.metadata.drop_all(
        bind=engine
    )


def get_test_db():
    """
    Creates a database session for a test.
    """

    setup_database()

    db = TestingSessionLocal()

    return db


# ---------------------------------------------------------
# Session tests
# ---------------------------------------------------------

def test_create_session():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Test Session"
        )

        assert session.id is not None
        assert session.title == "Test Session"

    finally:

        db.close()
        teardown_database()


def test_get_session():

    db = get_test_db()

    try:

        created_session = crud.create_session(
            db=db,
            title="Test Session"
        )

        session = crud.get_session(
            db=db,
            session_id=created_session.id
        )

        assert session is not None
        assert session.id == created_session.id
        assert session.title == "Test Session"

    finally:

        db.close()
        teardown_database()


def test_get_nonexistent_session():

    db = get_test_db()

    try:

        session = crud.get_session(
            db=db,
            session_id=999
        )

        assert session is None

    finally:

        db.close()
        teardown_database()


def test_update_session_title():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Old Title"
        )

        updated_session = crud.update_session_title(
            db=db,
            session_id=session.id,
            new_title="New Title"
        )

        assert updated_session is not None
        assert updated_session.title == "New Title"

    finally:

        db.close()
        teardown_database()


def test_update_nonexistent_session_title():

    db = get_test_db()

    try:

        result = crud.update_session_title(
            db=db,
            session_id=999,
            new_title="New Title"
        )

        assert result is None

    finally:

        db.close()
        teardown_database()


def test_delete_session():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Test Session"
        )

        session_id = session.id

        result = crud.delete_session(
            db=db,
            session_id=session_id
        )

        assert result is True

        deleted_session = crud.get_session(
            db=db,
            session_id=session_id
        )

        assert deleted_session is None

    finally:

        db.close()
        teardown_database()


def test_delete_nonexistent_session():

    db = get_test_db()

    try:

        result = crud.delete_session(
            db=db,
            session_id=999
        )

        assert result is False

    finally:

        db.close()
        teardown_database()


# ---------------------------------------------------------
# Message tests
# ---------------------------------------------------------

def test_add_message():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Test Session"
        )

        message = crud.add_message(
            db=db,
            session_id=session.id,
            role="user",
            content="Hello"
        )

        assert message.id is not None
        assert message.session_id == session.id
        assert message.role == "user"
        assert message.content == "Hello"

    finally:

        db.close()
        teardown_database()


def test_get_messages():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Test Session"
        )

        crud.add_message(
            db=db,
            session_id=session.id,
            role="user",
            content="First message"
        )

        crud.add_message(
            db=db,
            session_id=session.id,
            role="assistant",
            content="Second message"
        )

        messages = crud.get_messages(
            db=db,
            session_id=session.id
        )

        assert len(messages) == 2

        assert messages[0].content == "First message"
        assert messages[1].content == "Second message"

    finally:

        db.close()
        teardown_database()


# ---------------------------------------------------------
# Paper tests
# ---------------------------------------------------------

def test_add_paper():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        paper = crud.add_paper(
            db=db,
            session_id=session.id,
            filename="paper.pdf",
            stored_filename="abc123.pdf",
            file_path="data/paper.pdf"
        )

        assert paper.id is not None
        assert paper.session_id == session.id
        assert paper.filename == "paper.pdf"
        assert paper.stored_filename == "abc123.pdf"
        assert paper.file_path == "data/paper.pdf"

    finally:

        db.close()
        teardown_database()


def test_get_papers():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        crud.add_paper(
            db=db,
            session_id=session.id,
            filename="paper1.pdf",
            stored_filename="stored1.pdf",
            file_path="data/paper1.pdf"
        )

        crud.add_paper(
            db=db,
            session_id=session.id,
            filename="paper2.pdf",
            stored_filename="stored2.pdf",
            file_path="data/paper2.pdf"
        )

        papers = crud.get_papers(
            db=db,
            session_id=session.id
        )

        assert len(papers) == 2
        assert papers[0].filename == "paper1.pdf"
        assert papers[1].filename == "paper2.pdf"

    finally:

        db.close()
        teardown_database()


def test_delete_paper():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        paper = crud.add_paper(
            db=db,
            session_id=session.id,
            filename="paper.pdf",
            stored_filename="stored.pdf",
            file_path="data/paper.pdf"
        )

        result = crud.delete_paper(
            db=db,
            paper_id=paper.id
        )

        assert result is True

        papers = crud.get_papers(
            db=db,
            session_id=session.id
        )

        assert len(papers) == 0

    finally:

        db.close()
        teardown_database()


# ---------------------------------------------------------
# Conversation summary
# ---------------------------------------------------------

def test_update_conversation_summary():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        updated_session = (
            crud.update_conversation_summary(
                db=db,
                session_id=session.id,
                summary="Discussion about LLMs."
            )
        )

        assert updated_session is not None
        assert (
            updated_session.conversation_summary
            == "Discussion about LLMs."
        )

    finally:

        db.close()
        teardown_database()


# ---------------------------------------------------------
# Figure tests
# ---------------------------------------------------------

def test_save_figures():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        figures = [
            FigureInfo(
                session_id=session.id,
                paper_name="paper.pdf",
                page_number=3,
                figure_number="Fig. 1",
                figure_caption="System architecture.",
                image_path="data/figure1.png"
            ),
            FigureInfo(
                session_id=session.id,
                paper_name="paper.pdf",
                page_number=4,
                figure_number="Fig. 2",
                figure_caption="Model comparison.",
                image_path="data/figure2.png"
            )
        ]

        crud.save_figures(
            db=db,
            figures=figures
        )

        saved_figures = db.query(
            Figure
        ).all()

        assert len(saved_figures) == 2

        assert (
            saved_figures[0].figure_number
            == "Fig. 1"
        )

        assert (
            saved_figures[1].figure_number
            == "Fig. 2"
        )

    finally:

        db.close()
        teardown_database()


def test_get_figure_by_number():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        figure = Figure(
            session_id=session.id,
            paper_name="paper.pdf",
            page_number=3,
            figure_number="Fig. 1",
            figure_caption="System architecture.",
            image_path="data/figure1.png"
        )

        db.add(figure)
        db.commit()

        result = crud.get_figure_by_number(
            db=db,
            session_id=session.id,
            figure_number="Fig. 1"
        )

        assert result is not None
        assert result.figure_number == "Fig. 1"
        assert (
            result.figure_caption
            == "System architecture."
        )

    finally:

        db.close()
        teardown_database()


def test_get_nonexistent_figure():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        result = crud.get_figure_by_number(
            db=db,
            session_id=session.id,
            figure_number="Fig. 99"
        )

        assert result is None

    finally:

        db.close()
        teardown_database()


def test_get_figure_by_caption():

    db = get_test_db()

    try:

        session = crud.create_session(
            db=db,
            title="Research Session"
        )

        figure = Figure(
            session_id=session.id,
            paper_name="paper.pdf",
            page_number=3,
            figure_number="Fig. 1",
            figure_caption=(
                "System architecture of the proposed model."
            ),
            image_path="data/figure1.png"
        )

        db.add(figure)
        db.commit()

        result = crud.get_figure_by_caption(
            db=db,
            session_id=session.id,
            caption="System architecture"
        )

        assert result is not None
        assert result.figure_number == "Fig. 1"

    finally:

        db.close()
        teardown_database()