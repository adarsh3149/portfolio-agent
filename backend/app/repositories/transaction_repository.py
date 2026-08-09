from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm import selectinload
from sqlalchemy import func


from app.models.transaction import Transaction


class TransactionRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_user(
        self,
        user_id: int,
    ) -> list[Transaction]:

        statement = (
            select(Transaction)
            .options(
                selectinload(Transaction.asset),
            )
            .where(
                Transaction.user_id == user_id
            )
            .order_by(
                Transaction.transaction_date,
                Transaction.id,
            )
        )

        return list(
            self.db.scalars(statement)
        )

    def create(
        self,
        transaction: Transaction,
    ) -> Transaction:

        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)

        return transaction

    def count_by_user(
            self,
            user_id: int
    ) -> int:

        statment = (
            select(func.count())
            .select_from(Transaction)
            .where(
                Transaction.user_id == user_id
            )
        )

        return self.db.scalar(statment) or 0