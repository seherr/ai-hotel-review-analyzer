import requests
import streamlit as st


API_URL = "http://127.0.0.1:8000"
PAGE_SIZE = 10
SENTIMENT_LABELS = {
    "positive": "Olumlu",
    "neutral": "Nötr",
    "negative": "Olumsuz",
}


def show_analysis_form():
    with st.form("review_form"):
        review = st.text_area("Otel yorumu", placeholder="Oda temizdi, kahvaltı güzeldi.")
        submitted = st.form_submit_button("Analiz et ve kaydet", type="primary")

    if not submitted:
        return

    review = review.strip()
    if not review:
        st.warning("Analiz etmek için bir yorum yaz.")
        return

    try:
        with st.spinner("Yorum analiz ediliyor…"):
            response = requests.post(f"{API_URL}/analyze", json={"review": review}, timeout=(5, 60))
        if response.status_code == 503:
            st.error("Yorum şu anda analiz edilemedi. Biraz sonra tekrar dene.")
            return
        response.raise_for_status()
        result = response.json()
    except requests.Timeout:
        st.error("Analiz zaman aşımına uğradı. Tekrar göndermeden önce kaydedilip kaydedilmediğini kontrol et.")
        return
    except requests.ConnectionError:
        st.error("FastAPI’ye bağlanılamadı. Sunucunun 8000 numaralı portta çalıştığını kontrol et.")
        return
    except requests.RequestException:
        st.error("Analiz yanıtı alınamadı.")
        return

    st.success("Yorum ve analiz sonucu kaydedildi.")
    sentiment, confidence = st.columns(2)
    sentiment.metric("Duygu", SENTIMENT_LABELS[result["sentiment"]])
    confidence.metric("Güven puanı", f"{result['confidence']:.0%}")



def change_review_page(offset):
    st.session_state.review_offset = offset


def update_saved_review(review_id, text):
    if not text:
        st.warning("Yorum boş olamaz.")
        return

    try:
        with st.spinner("Yorum yeniden analiz ediliyor…"):
            response = requests.patch(
                f"{API_URL}/reviews/{review_id}", json={"text": text}, timeout=(5, 60)
            )
        if response.status_code == 503:
            st.error("Yeni metin analiz edilemedi. Biraz sonra tekrar dene.")
            return
        response.raise_for_status()
    except requests.Timeout:
        st.error("İstek zaman aşımına uğradı. Tekrar göndermeden önce yorumu kontrol et.")
        return
    except requests.RequestException:
        st.error("Yorum güncellenemedi. Bağlantıyı ve yorumun hâlâ kayıtlı olduğunu kontrol et.")
        return

    st.session_state.review_notice = "Yorum güncellendi ve yeniden analiz edildi."
    st.rerun()


def delete_saved_review(review_id):
    try:
        response = requests.delete(f"{API_URL}/reviews/{review_id}", timeout=5)
        response.raise_for_status()
    except requests.Timeout:
        st.error("İstek zaman aşımına uğradı. Tekrar denemeden önce listeyi kontrol et.")
        return
    except requests.RequestException:
        st.error("Yorum silinemedi. Bağlantıyı ve yorumun hâlâ kayıtlı olduğunu kontrol et.")
        return

    st.session_state.review_notice = "Yorum silindi."
    st.rerun()


def show_review_card(review):
    review_id = review["id"]
    with st.container(border=True):
        label = SENTIMENT_LABELS.get(review["sentiment"], "Analiz yok")
        st.caption(f"#{review_id} · {label}")
        st.text(review["review"])

        with st.expander("Düzenle"):
            with st.form(f"edit_review_{review_id}"):
                text = st.text_area("Yorum metni", value=review["review"])
                save = st.form_submit_button("Güncelle ve yeniden analiz et")
            if save:
                update_saved_review(review_id, text.strip())

        with st.expander("Sil"):
            confirmed = st.checkbox("Bu yorumu silmeyi onaylıyorum", key=f"confirm_delete_{review_id}")
            if st.button("Yorumu sil", key=f"delete_{review_id}", disabled=not confirmed) and confirmed:
                delete_saved_review(review_id)


def show_saved_reviews():
    st.subheader("Kayıtlı yorumlar")
    st.session_state.setdefault("review_offset", 0)

    selected = st.selectbox(
        "Duygu filtresi",
        [None, *SENTIMENT_LABELS],
        format_func=lambda value: SENTIMENT_LABELS.get(value, "Tümü"),
        on_change=change_review_page,
        args=(0,),
    )
    offset = st.session_state.review_offset
    params = {"limit": PAGE_SIZE + 1, "offset": offset}
    if selected is not None:
        params["sentiment"] = selected

    try:
        response = requests.get(f"{API_URL}/reviews", params=params, timeout=5)
        response.raise_for_status()
        reviews = response.json()
    except requests.RequestException:
        st.error("Kayıtlı yorumlar yüklenemedi. FastAPI bağlantısını kontrol et.")
        return

    if not reviews and offset:
        change_review_page(0)
        st.rerun()

    notice = st.session_state.pop("review_notice", None)
    if notice:
        st.success(notice)
    if not reviews:
        st.info("Bu sayfada gösterilecek yorum yok.")

    for review in reviews[:PAGE_SIZE]:
        show_review_card(review)

    previous, page, following = st.columns(3)
    previous.button(
        "Önceki",
        disabled=offset == 0,
        on_click=change_review_page,
        args=(max(0, offset - PAGE_SIZE),),
    )
    page.caption(f"Sayfa {offset // PAGE_SIZE + 1}")
    following.button(
        "Sonraki",
        disabled=len(reviews) <= PAGE_SIZE,
        on_click=change_review_page,
        args=(offset + PAGE_SIZE,),
    )


def show_report():
    st.subheader("Analiz raporu")

    try:
        response = requests.get(f"{API_URL}/report", timeout=5)
        response.raise_for_status()
        report = response.json()
    except requests.RequestException:
        st.error("Rapor yüklenemedi. FastAPI bağlantısını kontrol et.")
        return

    total = report["total_completed"]
    confidence = report["average_confidence"]
    summary, average = st.columns(2)
    summary.metric("Tamamlanan analiz", total)
    average.metric("Ortalama güven puanı", "—" if confidence is None else f"{confidence:.0%}")

    if total == 0:
        st.info("Henüz tamamlanmış analiz yok.")
        return

    distribution = report["sentiment_distribution"]
    for column, (sentiment, label) in zip(st.columns(3), SENTIMENT_LABELS.items()):
        column.metric(label, distribution.get(sentiment, 0))


def main():
    st.set_page_config(page_title="Otel Yorum Analizi")
    st.title("Otel yorum analizi")
    show_analysis_form()
    show_report()
    show_saved_reviews()


if __name__ == "__main__":
    main()
