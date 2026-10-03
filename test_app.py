import tempfile
import unittest
from pathlib import Path

from app import create_app


class ExplorerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.app = create_app(
            {"TESTING": True, "DATABASE": str(Path(self.temp_dir.name) / "test.db")}
        )
        self.client = self.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_homepage_shows_searchable_topics(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Yamna", response.data)
        self.assertIn(b"Rus", response.data)
        self.assertIn(b"ukraine-map.png", response.data)
        self.assertIn(b"13</strong> curated connections", response.data)
        self.assertLess(response.data.find(b"Yamna"), response.data.find(b"Rus"))

    def test_search_filters_topics(self):
        response = self.client.get("/?q=Antiquity")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ancient Athens", response.data)
        self.assertNotIn(b"Rus</h3>", response.data)

    def test_topic_page_shows_explained_and_cited_connections(self):
        response = self.client.get("/topic/rus")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"<h2>Rus</h2>", response.data)
        self.assertIn(b"Slavic peoples", response.data)
        self.assertIn(b"Vikings", response.data)
        self.assertIn(b"Byzantium", response.data)
        self.assertIn(b"Formation included", response.data)
        self.assertIn(b"https://uhgi.org/", response.data)

    def test_topic_explanation_citation_tokens_become_links(self):
        response = self.client.get("/topic/yamna")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'https://www.nature.com/articles/s41586-024-08531-5', response.data)
        self.assertIn(b'nature+1', response.data)
        self.assertIn(b'https://www.science.org/content/article/nomadic-herders-left-strong-genetic-mark-europeans-and-asians', response.data)

    def test_unknown_topic_returns_not_found(self):
        response = self.client.get("/topic/not-a-topic")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
