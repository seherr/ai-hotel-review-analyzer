
from processor  import process_reviews
from database import init_db, save_review, get_reviews
from reports import generate_report


init_db()

reviews = ["Otel çok temizdi.", 
           "Personel kabaydı."]

# 1. Yorumları analiz et.

results = process_reviews(reviews)

# 2. Analiz sonuçlarını veritabanına kaydet. 

for result in results:
    save_review(result)

# 3. Db deki kayıtları getir.

saved_reviews = get_reviews()

# 4. Kayıtları ekrana yazdır

for review in saved_reviews:
    print(review)
    
report = generate_report()
print(report)