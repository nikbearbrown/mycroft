from typing import Dict, List
import ssl
from GoogleNews import GoogleNews
import feedparser
import newspaper
import uuid
from transformers import pipeline
import tomllib
from time import mktime
from datetime import datetime


def fetch_normalize_data(
    feed_url: str,
    lib: str,
    last_updated: float = None,
    search_terms: List[str] = ["Artificial Intelligence"],
):
    def add_tag(item: Dict, source: str):
        # Add source tag for traceability
        item["source"] = source
        return item

    if hasattr(ssl, "_create_unverified_context"):
        ssl._create_default_https_context = ssl._create_unverified_context
    if lib == "googlenews":
        try:
            googlenews = GoogleNews(lang="en", period="7d", region="US")
            googlenews.search(" ".join(search_terms))
            return [add_tag(normalize_data(i), lib) for i in googlenews.results()]
        except Exception as e:
            raise e
    elif lib == "feedparser":
        try:
            entries = []
            # for feed_url in sources:
            news_feed = feedparser.parse(feed_url)
            feed_updated = news_feed.feed.get("updated_parsed") or news_feed.feed.get(
                "published_parsed"
            )
            print("Feed updated:", feed_updated, type(feed_updated))
            if last_updated and feed_updated:
                # Make sure feed_updated exists and is newer than last_updated
                if mktime(feed_updated) > last_updated:
                    entries.extend(news_feed.get("entries", []))
            else:
                # No last_updated given or feed_updated not available → always include entries
                entries.extend(news_feed.get("entries", []))
            return {
                "articles": [
                    add_tag(normalize_data(item), f"{lib}/{feed_url}")
                    for item in entries
                ],
                "last_updated": (
                    (mktime(feed_updated))
                    if feed_updated
                    else mktime(datetime.now().timetuple())
                ),
                "feed_url": feed_url,
            }
        except Exception as e:
            raise e


def get_sources(key: str, path="sources.toml"):
    with open(path, "rb") as f:
        sources = tomllib.load(f)
    try:
        feed_urls = sources.get(key, [])
        return feed_urls
    except Exception as e:
        print(e)


def normalize_data(input: Dict):
    try:
        news_article = {
            "id": uuid.uuid4(),
            "title": input.get("title", ""),
            "content": input.get("summary", "") or input.get("desc", ""),
            "url": clean_link(input.get("link", "")),
            "published_date": input.get("published", "") or input["datetime"],
            "updated_date": input.get("updated_date", ""),
        }
        return news_article
    except Exception as e:
        print("error normalizing article", e)


def clean_link(link: str):
    if "&ved=" in link:
        link = link[: link.rfind("&ved=")].rstrip("/")
    if "&url=" in link:
        link = link[link.find("&url=") + 5 :]
    if "&ct=" in link:
        link = link[: link.find("&ct=")].rstrip("/")
    return link


def parse_article(input: Dict):
    if hasattr(ssl, "_create_unverified_context"):
        ssl._create_default_https_context = ssl._create_unverified_context
    news_article = {}
    link = input.get("url", "")
    try:
        newspaper_article = newspaper.article(url=link)
        newspaper_article.download()
        news_article = {
            "id": uuid.uuid4(),
            "title": newspaper_article.title,
            "content": newspaper_article.text,
            "url": newspaper_article.canonical_link,
            "published_date": newspaper_article.publish_date,
            "source_name": newspaper_article.source_url,
            "site_name": newspaper_article.meta_site_name,
            "fetch_lib": input.get("source", ""),
        }
        return news_article
    except Exception as e:
        print("error parsing article", e)


def finbert_pipeline():
    print("Creating pipe")
    pipe = pipeline("text-classification", model="ProsusAI/finbert")
    return pipe
