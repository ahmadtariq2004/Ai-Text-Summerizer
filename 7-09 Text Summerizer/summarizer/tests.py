from unittest.mock import patch

import requests
from django.test import TestCase
from rest_framework.test import APIClient


class SummarizeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.text = "This is a sufficiently long piece of text that gives the model enough context to create a useful and focused summary for the reader. It explains the central idea clearly and includes practical examples that make the main point easier to understand. The summary should stay faithful to the source while highlighting the most important information for the reader."

    @patch("summarizer.views.summarize_with_qwen", return_value="A focused summary.")
    def test_summarize_returns_model_output(self, summarize):
        response = self.client.post("/api/summarize/", {"text": self.text, "style": "balanced"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"], "A focused summary.")
        summarize.assert_called_once()

    @patch("summarizer.services.requests.post", side_effect=requests.exceptions.ConnectionError)
    def test_falls_back_to_local_summary_when_ollama_is_unavailable(self, _):
        summary = __import__("summarizer.services", fromlist=["summarize_with_qwen"]).summarize_with_qwen(self.text, "balanced")
        self.assertIn("summary", summary.lower())
        self.assertTrue(len(summary) > 40)

    @patch("summarizer.services.requests.post", side_effect=requests.exceptions.HTTPError("model not found"))
    def test_falls_back_when_ollama_returns_http_error(self, _):
        summary = __import__("summarizer.services", fromlist=["summarize_with_qwen"]).summarize_with_qwen(self.text, "balanced")
        self.assertIn("key takeaways", summary.lower())
        self.assertTrue(len(summary) > 40)

    def test_short_text_is_rejected(self):
        response = self.client.post("/api/summarize/", {"text": "Too short."}, format="json")
        self.assertEqual(response.status_code, 400)
