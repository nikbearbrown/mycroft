import pytest
from .utils import (
    fetch_normalize_data,
    normalize_data,
    clean_link,
    parse_article,
    get_sources,
)
import uuid

# Mock data for testing
MOCK_GOOGLE_NEWS_RESULT = {
    "title": "Test Google News Article",
    "link": "http://example.com/googlenews?&url=http://real.example.com/googlenews_article&ved=somecode",
    "datetime": "2023-10-27 10:00:00",
    "desc": "Description from Google News",
}

MOCK_FEEDPARSER_ENTRY = {
    "title": "Test Feedparser Article",
    "link": "http://example.com/feedparser_article&ct=somecode",
    "summary": "This is a summary of a Feedparser article.",
    "published": "Fri, 27 Oct 2023 10:00:00 GMT",
    "updated_date": "Fri, 27 Oct 2023 11:00:00 GMT",
}

MOCK_NEWSPAPER_ARTICLE_DATA = {
    "url": "http://example.com/newspaper_article",
    "title": "Newspaper Article Title",
    "text": "Full content of the newspaper article.",
    "canonical_link": "http://example.com/newspaper_article",
    "publish_date": "2023-10-27 12:00:00",
    "source_url": "http://example.com",
    "meta_site_name": "Example Site",
}


# Mock the newspaper.article to avoid actual web requests
class MockNewspaperArticle:
    def __init__(self, url):
        self.url = url
        self.title = MOCK_NEWSPAPER_ARTICLE_DATA["title"]
        self.text = MOCK_NEWSPAPER_ARTICLE_DATA["text"]
        self.canonical_link = MOCK_NEWSPAPER_ARTICLE_DATA["canonical_link"]
        self.publish_date = MOCK_NEWSPAPER_ARTICLE_DATA["publish_date"]
        self.source_url = MOCK_NEWSPAPER_ARTICLE_DATA["source_url"]
        self.meta_site_name = MOCK_NEWSPAPER_ARTICLE_DATA["meta_site_name"]

    def download(self):
        pass  # No actual download needed for mock

    def parse(self):
        pass  # No actual parsing needed for mock


@pytest.fixture(autouse=True)
def mock_newspaper_article(monkeypatch):
    def mock_article(url):
        return MockNewspaperArticle(url)

    monkeypatch.setattr("newspaper.article", mock_article)


def test_get_sources():
    sources = get_sources("feedparser", "test_sources.toml")
    assert sources != None
    assert sources == [
        "https://www.google.com/alerts/feeds/07049913474957125298/12956790815811234855"
    ]


def test_normalize_data_googlenews():
    normalized = normalize_data(MOCK_GOOGLE_NEWS_RESULT)
    assert isinstance(normalized["id"], uuid.UUID)
    assert normalized["title"] == "Test Google News Article"
    assert normalized["content"] == "Description from Google News"
    assert normalized["url"] == "http://real.example.com/googlenews_article"
    assert normalized["published_date"] == "2023-10-27 10:00:00"
    assert normalized["updated_date"] == ""


def test_normalize_data_feedparser():
    normalized = normalize_data(MOCK_FEEDPARSER_ENTRY)
    assert isinstance(normalized["id"], uuid.UUID)
    assert normalized["title"] == "Test Feedparser Article"
    assert normalized["content"] == "This is a summary of a Feedparser article."
    assert normalized["url"] == "http://example.com/feedparser_article"
    assert normalized["published_date"] == "Fri, 27 Oct 2023 10:00:00 GMT"
    assert normalized["updated_date"] == "Fri, 27 Oct 2023 11:00:00 GMT"
