"""Integration tests that hit the real fastcrw.com API."""

from __future__ import annotations

import os

import pytest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not os.getenv("CRW_API_KEY"),
        reason="CRW_API_KEY not set",
    ),
]

API_URL = "https://fastcrw.com/api"


def _api_key() -> str:
    return os.environ["CRW_API_KEY"]


def test_scrape_real_url():
    from crewai_crw import CrwScrapeWebsiteTool

    tool = CrwScrapeWebsiteTool(api_url=API_URL, api_key=_api_key())
    result = tool._run(url="https://example.com")

    assert isinstance(result, str)
    assert len(result) > 0


def test_crawl_real_url():
    from crewai_crw import CrwCrawlWebsiteTool

    tool = CrwCrawlWebsiteTool(
        api_url=API_URL,
        api_key=_api_key(),
        config={"maxPages": 2},
        max_wait=60,
    )
    result = tool._run(url="https://example.com")

    assert isinstance(result, str)
    assert len(result) > 0


def test_map_real_url():
    from crewai_crw import CrwMapWebsiteTool

    tool = CrwMapWebsiteTool(api_url=API_URL, api_key=_api_key())
    result = tool._run(url="https://example.com")

    assert isinstance(result, str)
    assert len(result) > 0
    # Should contain at least one URL
    assert "http" in result


def test_search_real_query():
    from crewai_crw import CrwSearchWebTool

    tool = CrwSearchWebTool(api_url=API_URL, api_key=_api_key())
    result = tool._run(query="python web scraping")

    assert isinstance(result, str)
    assert len(result) > 0


def test_scrape_with_js_rendering():
    from crewai_crw import CrwScrapeWebsiteTool

    tool = CrwScrapeWebsiteTool(
        api_url=API_URL,
        api_key=_api_key(),
        config={"renderJs": True},
    )
    result = tool._run(url="https://example.com")

    assert isinstance(result, str)
    assert len(result) > 0
