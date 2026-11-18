# birden fazla yorum işleme.

from app.analyzer import analyze_review



reviews = ["Otel temizdi.","Personel kabaydı." ]


def process_reviews(reviews):

    """
    Birden fazla yorumu analiz ediyor.
    
    """
    result_list = []

    for review in reviews:
        result = retry_analysis(review)

        if result is not None:
            completed = {
            "review" : review,
            "sentiment": result.sentiment,
            "confidence" : result.confidence,
            "status" : "completed"
            }
            result_list.append(completed)
        
        else:
            failed = {
            "review" : review,
            "sentiment": None,
            "confidence" : None,
            "status" : "failed"
            }
        
            result_list.append(failed)

    return result_list


def retry_analysis(review):
    """
    Bir yorumu en fazla 3 kez analiz ediyor.

    """
    for attempt in range(3):

        result = analyze_review(review)

        if result is not None:
            print("Analiz başarılı.")
            return result

        else:
            print("Deneme:" , attempt + 1)
           
    return None        
            
            
