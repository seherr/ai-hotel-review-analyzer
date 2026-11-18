


from unittest.mock import patch
from app.processor import retry_analysis


def test_retry_first_attempt():
    """İlk denemede başarılı analiz."""

    with patch("app.processor.analyze_review") as mock_analyzer:
        mock_analyzer.side_effect = ["positive"]

        result = retry_analysis("Otel temizdi.")

        assert result == "positive"
        assert mock_analyzer.call_count == 1


def test_retry_second_attempt():
    """İlk deneme başarısız, ikinci deneme başarılı."""

    with patch("app.processor.analyze_review") as mock_analyzer:
        mock_analyzer.side_effect = [None, "positive"]

        result = retry_analysis("Otel temizdi.")

        assert result == "positive"
        assert mock_analyzer.call_count == 2


def test_retry_all_failed():
    """Üç denemenin tamamı başarısız."""

    with patch("app.processor.analyze_review") as mock_analyzer:
        mock_analyzer.side_effect = [None, None, None]

        result = retry_analysis("Otel temizdi.")

        assert result is None
        assert mock_analyzer.call_count == 3
