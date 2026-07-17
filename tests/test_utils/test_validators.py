"""Tests for validator utilities."""

from src.utils.validators import sanitize_text, validate_akd_name, validate_sentiment


class TestValidateAKDName:
    """Test AKD name validation against the master JSON file."""

    def test_valid_komisi_names(self) -> None:
        assert validate_akd_name("Komisi I")
        assert validate_akd_name("Komisi XI")

    def test_valid_badan_names(self) -> None:
        assert validate_akd_name("BURT")
        assert validate_akd_name("Baleg")
        assert validate_akd_name("BAKN")
        assert validate_akd_name("BKSAP")
        assert validate_akd_name("MKD")

    def test_valid_pimpinan(self) -> None:
        assert validate_akd_name("Pimpinan DPR")

    def test_invalid_names(self) -> None:
        assert not validate_akd_name("Komisi XII")
        assert not validate_akd_name("Invalid AKD")
        assert not validate_akd_name("")
        assert not validate_akd_name("komisi i")  # Case sensitive


class TestValidateSentiment:
    """Test sentiment value validation."""

    def test_valid_sentiments(self) -> None:
        assert validate_sentiment("Positif")
        assert validate_sentiment("Negatif")
        assert validate_sentiment("Netral")

    def test_invalid_sentiments(self) -> None:
        assert not validate_sentiment("Unknown")
        assert not validate_sentiment("positif")  # Case sensitive
        assert not validate_sentiment("")


class TestSanitizeText:
    """Test text sanitization."""

    def test_strips_html_tags(self) -> None:
        assert sanitize_text("<b>Hello</b> world") == "Hello world"

    def test_normalizes_whitespace(self) -> None:
        assert sanitize_text("hello   world") == "hello world"

    def test_combined(self) -> None:
        assert sanitize_text("<p>Hello</p>   <b>world</b>") == "Hello world"

    def test_preserves_normal_text(self) -> None:
        assert sanitize_text("Normal text here") == "Normal text here"

    def test_strips_leading_trailing(self) -> None:
        assert sanitize_text("  hello  ") == "hello"
