

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

