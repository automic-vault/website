#!/usr/bin/env python3
"""Generate the JSON Feed in the blog index's editorial order."""
from html.parser import HTMLParser
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://www.automicvault.com"


class Posts(HTMLParser):
    def __init__(self):
        super().__init__()
        self.heading = False
        self.path = None
        self.title = []
        self.items = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "h2":
            self.heading = True
        if tag == "a" and self.heading and attrs.get("href", "").startswith("/blog/"):
            self.path = attrs["href"]
            self.title = []

    def handle_data(self, data):
        if self.path:
            self.title.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.path:
            title = " ".join("".join(self.title).split())
            self.items.append({"id": ORIGIN + self.path, "url": ORIGIN + self.path,
                               "title": title, "content_text": title})
            self.path = None
        if tag == "h2":
            self.heading = False


def feed():
    parser = Posts()
    parser.feed((ROOT / "www/blog/index.html").read_text())
    assert parser.items, "Blog index has no article headings"
    return {"version": "https://jsonfeed.org/version/1.1", "title": "Automic Vault Blog",
            "home_page_url": ORIGIN + "/blog/", "feed_url": ORIGIN + "/blog/index.json",
            "items": parser.items}


if __name__ == "__main__":
    (ROOT / "www/blog/index.json").write_text(json.dumps(feed(), ensure_ascii=False, indent=2) + "\n")
