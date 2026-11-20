import pytest
from fastapi.testclient import TestClient
import api
from app import database

def test_analyze_failure_returns_503_without_saving(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))

    def failed_analysis(reviews):
        return [{"status": "failed"}]

    def unexpected_save(result):
        raise AssertionError("Başarısız analiz kaydedilmedi.")

    monkeypatch.setattr(api,"process_reviews", failed_analysis)
    monkeypatch.setattr(api,"save_review", unexpected_save)

    with TestClient(api.app) as client:
        response = client.post("/analyze", json = {"review":"Oda temizdi."})

    assert response.status_code == 503
    assert response.json() == {"detail": "Yorum analiz edilemedi."}

def test_analyze_success_saves_review(monkeypatch, tmp_path):

    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()

    result = {
        "review": "Oda temizdi.",
        "sentiment": "positive",
        "confidence": 0.95,
        "status": "completed",
    }
    monkeypatch.setattr(api, "process_reviews", lambda reviews: [result])

    with TestClient(api.app) as client:
        response = client.post("/analyze", json={"review": "Oda temizdi."})
        assert response.status_code == 200

        saved = client.get("/reviews/1")
        assert saved.status_code == 200
        assert saved.json() == {"id": 1, **result}

def test_delete_removes_review(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()
    database.save_review({
        "review": "Silinecek test yorumu.",
        "sentiment": "neutral",
        "confidence": 0.90,
        "status": "completed",
    })

    with TestClient(api.app) as client:
        deleted = client.delete("/reviews/1")
        assert deleted.status_code == 200
        assert deleted.json() == {"deleted_id": 1}

        missing = client.get("/reviews/1")
        assert missing.status_code == 404


def test_patch_updates_text_and_sentiment(monkeypatch, tmp_path):
    monkeypatch.setattr(database, "DB_PATH", str(tmp_path / "test.db"))
    database.init_db()
    database.save_review({
        "review": "Personel kabaydı.",
        "sentiment": "negative",
        "confidence": 0.90,
        "status": "completed",
    })

    new_result = {
        "review": "Personel güler yüzlüydü.",
        "sentiment": "positive",
        "confidence": 0.98,
        "status": "completed",
    }

    def analyze(reviews):
        assert reviews == [new_result["review"]]
        return [new_result]

    monkeypatch.setattr(api, "process_reviews", analyze)

    with TestClient(api.app) as client:
        updated = client.patch("/reviews/1", json={"text": new_result["review"]})
        assert updated.status_code == 200

        saved = client.get("/reviews/1")
        assert saved.status_code == 200
        assert saved.json() == {"id": 1, **new_result}


def test_startup_initializes_database(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    with TestClient(api.app) as client:
        reviews = client.get("/reviews")
        report = client.get("/report")

    assert reviews.status_code == 200
    assert reviews.json() == []
    assert report.status_code == 200
    assert report.json() == {
        "total_completed": 0,
        "sentiment_distribution": {},
        "average_confidence": None,
    }


def test_list_reviews_filters_and_paginates(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    with TestClient(api.app) as client:
        for review, sentiment, confidence in [
            ("Oda kirliydi.", "negative", 0.90),
            ("Kahvaltı güzeldi.", "positive", 0.80),
            ("Oda gürültülüydü.", "negative", 0.70),
        ]:
            database.save_review({
                "review": review,
                "sentiment": sentiment,
                "confidence": confidence,
                "status": "completed",
            })

        response = client.get(
            "/reviews",
            params={"sentiment": "negative", "limit": 1, "offset": 1},
        )

    assert response.status_code == 200
    assert [(row["id"], row["sentiment"]) for row in response.json()] == [
        (3, "negative")
    ]


def test_report_summarizes_completed_reviews(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    with TestClient(api.app) as client:
        for sentiment, confidence, status in [
            ("positive", 0.90, "completed"),
            ("negative", 0.60, "completed"),
            (None, None, "failed"),
        ]:
            database.save_review({
                "review": "Test yorumu.",
                "sentiment": sentiment,
                "confidence": confidence,
                "status": status,
            })

        response = client.get("/report")

    assert response.status_code == 200
    assert response.json() == {
        "total_completed": 2,
        "sentiment_distribution": {"positive": 1, "negative": 1},
        "average_confidence": pytest.approx(0.75),
    }
