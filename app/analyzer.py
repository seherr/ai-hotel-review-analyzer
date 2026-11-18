
import os 
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import (SystemMessage, HumanMessage)
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

def get_model(model_name,provider,api_key):
    gemini_model = init_chat_model(model = model_name,
        model_provider = provider,
        api_key = api_key)
              
    return gemini_model

llm = get_model("gemini-3.5-flash-lite", "google_genai", api_key)

class ReviewAnalysis(BaseModel):

    sentiment : Literal["positive", "negative","neutral"]
    confidence: float = Field(ge=0, le=1)

structured_model = llm.with_structured_output(ReviewAnalysis)
    

def analyze_review(review):

    messages = [SystemMessage ( content = "Otel yorumlarını analiz et ve sadece positive, negative veya neutral yanıtlarından birini ver. Confidence değeri oluştur ve 0 ile 1 arasında bir değer olsun.  "),
                HumanMessage (content = review)
                ]
    
    try:     
        response = structured_model.invoke(messages)
        return response
    except Exception as error:
        print("Hata oluştu", error)
        return None


