from app.models.user import User
from app.repositories.user_repository import UserRepository

def test_get_all_returns_users(
    db_session,
):
    user_1 = User(
        name="User One",
        email="user_one@example.com",
        password_hash="password",
    )

    user_2 = User(
        name="User Two",
        email="user_two@example.com",
        password_hash="password",
    )

    db_session.add_all([
        user_1,
        user_2,
    ])

    db_session.commit()

    repository = UserRepository(
        db_session
    )

    users = repository.get_all()

    assert len(users) == 2

    assert [
        user.email
        for user in users
    ] == [
        "user_one@example.com",
        "user_two@example.com",
    ]
