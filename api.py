
from fastapi import FastAPI, HTTPException, Query
from app.reports import generate_report
from app.processor import process_reviews
from app.database import save_review, get_reviews, get_review_by_id, delete_review_by_id
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
def list_reviews(
    sentiment: str | None = None,
    limit: int=Query(default=10, ge=1,le=100),
    offset: int=Query(default=0, ge=0)
    ):

    if sentiment is not None:
        sentiment = sentiment.strip()

    return  get_reviews(sentiment,limit,offset)


@app.get("/reviews/{review_id}")
def get_review(review_id: int):

    result = get_review_by_id(review_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail = "Yorum bulunamadı.")

    return result

@app.delete("/reviews/{review_id}")
def delete_review(review_id: int):
    if not delete_review_by_id(review_id):
        raise HTTPException(
            status_code=404,
            detail = "Yorum bulunamadı."
        )
    return {"deleted_id": review_id}
