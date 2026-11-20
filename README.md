# AI Hotel Review Analyzer

Otel yorumlarının duygu durumunu Gemini ile analiz eden bir FastAPI uygulaması. Yorumlar ve analiz sonuçları yerel bir SQLite veritabanında saklanır.

## Kurulum

Python 3.10 ile doğrulandı. Proje klasöründe şu komutları çalıştır:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

`.env` dosyasındaki `GOOGLE_API_KEY=` satırına kendi Gemini API anahtarını yaz.

## API'yi çalıştırma

```bash
python -m uvicorn api:app --reload
```

FastAPI ilk açılışta `hotel_reviews.db` dosyasını hazırlar. API'yi [Swagger arayüzünden](http://127.0.0.1:8000/docs) veya Postman ile deneyebilirsin.

| İstek | İşlem | Örnek JSON gövdesi |
| --- | --- | --- |
| `POST /analyze` | Yorumu analiz et ve kaydet | `{"review": "Oda temizdi."}` |
| `GET /reviews?sentiment=positive&limit=10&offset=0` | Yorumları filtrele ve listele | |
| `GET /reviews/1` | Bir yorumu getir | |
| `PATCH /reviews/1` | Yorumu güncelle ve yeniden analiz et | `{"text": "Oda çok temizdi."}` |
| `DELETE /reviews/1` | Bir yorumu sil | |
| `GET /report` | Duygu dağılımını ve ortalama güven puanını getir | |

Örnekler için önce bir test yorumu kaydet. `GET /reviews` yanıtında gördüğün ID'yi tek yorum isteklerinde kullan.

## Streamlit arayüzünü açma

FastAPI çalışırken proje klasöründe ikinci bir terminal aç:

```bash
source .venv/bin/activate
python -m streamlit run streamlit_app.py
```

Arayüzü tarayıcıda [localhost:8501](http://localhost:8501) adresinde aç. Yorum yazıp **Analiz et ve kaydet** düğmesine bas. Sonuçta duygu etiketi ve güven puanı görünür. **Kayıtlı yorumlar** bölümünde duyguya göre filtreleyebilir ve sayfalar arasında gezebilirsin. Her kartta yorumu düzenleyip yeniden analiz edebilir veya onay vererek silebilirsin.

**Analiz raporu** bölümünde tamamlanan analiz sayısı, duygu dağılımı ve ortalama güven puanı görünür.

## Testler

```bash
python -m pytest -q
```

API testleri geçici SQLite dosyaları ve örnek analiz sonuçları kullanır. Test sırasında Gemini'ye istek gönderilmez.
