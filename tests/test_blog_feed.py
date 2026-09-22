import json
import pathlib
import runpy
import unittest
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]


class BlogFeedTests(unittest.TestCase):
    def test_feed_matches_blog_and_links_to_existing_articles(self):
        generated = runpy.run_path(str(ROOT / 'scripts/generate-blog-feed.py'))['feed']()
        self.assertEqual(generated, json.loads((ROOT / 'www/blog/index.json').read_text()))
        self.assertGreater(len(generated['items']), 2)
        self.assertEqual(len(generated['items']), len({p['id'] for p in generated['items']}))
        for post in generated['items']:
            url = urlparse(post['url'])
            self.assertEqual(url.netloc, 'www.automicvault.com')
            self.assertTrue((ROOT / 'www' / url.path.lstrip('/') / 'index.html').is_file())
            self.assertTrue(post['title'])
