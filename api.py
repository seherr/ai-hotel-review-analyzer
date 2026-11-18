
from fastapi import FastAPI, HTTPException
from app.reports import generate_report
from app.processor import process_reviews
from app.database import save_review, get_reviews
from pydantic import BaseModel,Field

class ReviewRequest(BaseModel):
    review: str = Field(min_length=1)

app = FastAPI()

@app.get("/")
def home():
    return {"message": "AI Hotel Review Analyzer API çalışıyor"}

@app.get("/report")
def get_report():
    return generate_report()

@app.post("/analyze")
def analyze(request: ReviewRequest):

    review = request.review.strip()

    if not review:
        raise HTTPException(
            status_code = 400,
            detail = "Geçersiz karakter , Yorum boş olamaz."

        )

    results = process_reviews([request.review])
    result = results[0]
    save_review(result)

    if result["status"] == "failed":
        raise HTTPException(
            status = 503,
            detail = "Yorum analiz edilmedi."
        )


    return result

@app.get("/reviews")
def list_reviews(sentiment: str | None = None, limit: int=10, offset: int=0):

    if sentiment is not None:
        sentiment = sentiment.strip()

    results = get_reviews(sentiment,limit,offset)

    print("Veritabanından gelen: ", results)

    return results

