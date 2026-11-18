
import sqlite3
from app.database import DB_PATH

def get_sentiment_distribution():

    connection = sqlite3.connect(DB_PATH)

    try:
        cursor = connection.execute("""
            SELECT sentiment, COUNT(*)
            FROM reviews
            WHERE status = 'completed'
            GROUP BY sentiment
            """)
        return dict(cursor.fetchall())
    
    finally:
        connection.close()

def get_average_confidence():
    connection = sqlite3.connect(DB_PATH)

    try: 

        cursor = connection.execute("""
            SELECT AVG(confidence) 
            FROM reviews 
            WHERE status == 'completed'
            """)

        result = cursor.fetchone()
        return result[0]
    
    finally:
        connection.close()

def generate_report():

    distribution = get_sentiment_distribution()
    average_confidence = get_average_confidence()

    total_completed  = sum(distribution.values())

    report = {

        "total_completed": total_completed,
        "sentiment_distribution": distribution,
        "average_confidence": average_confidence
    }

    return report