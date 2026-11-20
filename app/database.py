

import sqlite3

DB_PATH = "hotel_reviews.db"

def init_db():

    with sqlite3.connect(DB_PATH) as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS reviews(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                review TEXT NOT NULL,
                sentiment TEXT,
                confidence REAL,
                status TEXT NOT NULL
                           ) 
            """)
        

def save_review(result):
    connection = sqlite3.connect(DB_PATH)

    try:

        connection.execute("""

        INSERT INTO reviews (review, sentiment, confidence, status)
        VALUES(?,?,?,?)
                           
        """,(
            result["review"],
            result["sentiment"],
            result["confidence"],
            result["status"]
        ))

        connection.commit()
    finally:
        connection.close()


def get_reviews(sentiment = None, limit = 10, offset = 0):

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:
        if sentiment is None:
            cursor = connection.execute(
                """SELECT * From reviews
                   ORDER BY id
                   LIMIT ?
                   OFFSET  ?
                """,
                (limit,offset)
            )
        else:
            cursor= connection.execute(
                """
                SELECT * From reviews
                WHERE sentiment = ?
                ORDER BY id
                LIMIT  ?
                OFFSET  ?
               
                 
                """,

            (sentiment,limit, offset)
            )

        return [dict(row) for row in cursor.fetchall()]
        
    finally:
        connection.close()


def get_negative_reviews():

    connection = sqlite3.connect(DB_PATH)

    try: 
        cursor = connection.execute(
            "SELECT * FROM reviews WHERE sentiment = ?",
            ("negative",)
        )

    finally: 
        connection.close()

def get_review_by_id(review_id):

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row

    try:

        cursor = connection.execute(
            """
            SELECT * FROM reviews
            WHERE id = ?

            """,
            (review_id,)
        )
        row = cursor.fetchone()

        if row is None:
            return None
        return dict(row)

    finally:
        connection.close()

def delete_review_by_id(review_id: int) -> bool:
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute(
            """
            DELETE FROM reviews
            WHERE id = ?
            """,
            (review_id,),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()

def upgrade_review_by_id(review_id: int, result: dict) -> bool:
    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute(
            """
            UPDATE reviews
            SET review = ?, sentiment = ?, confidence = ?, status = ?
            WHERE id = ?
            """,
            (
                result["review"],
                result["sentiment"],
                result["confidence"],
                result["status"],
                review_id,
            ),
        )

        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()
