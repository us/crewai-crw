"""Unit tests for CRW CrewAI tools with mocked CrwClient."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# --- CrwScrapeWebsiteTool Tests ---


@patch("crewai_crw.tools._make_client")
def test_scrape_returns_markdown(mock_make_client):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_client = MagicMock()
    mock_client.scrape.return_value = {
        "markdown": "# Hello World\n\nThis is a test.",
        "metadata": {"title": "Test", "sourceURL": "https://example.com"},
    }
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "# Hello World\n\nThis is a test."
    mock_client.scrape.assert_called_once()
    call_kwargs = mock_client.scrape.call_args
    assert call_kwargs[0][0] == "https://example.com"


@patch("crewai_crw.tools._make_client")
def test_scrape_with_custom_config(mock_make_client):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_client = MagicMock()
    mock_client.scrape.return_value = {"markdown": "content"}
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool(
        config={
            "formats": ["markdown", "html"],
            "onlyMainContent": False,
            "renderJs": True,
        }
    )
    tool._run(url="https://example.com")

    call_kwargs = mock_client.scrape.call_args
    assert call_kwargs[1].get("formats") == ["markdown", "html"]
    assert call_kwargs[1].get("only_main_content") is False
    assert call_kwargs[1].get("renderJs") is True


@patch("crewai_crw.tools._make_client")
def test_scrape_with_api_key(mock_make_client):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_client = MagicMock()
    mock_client.scrape.return_value = {"markdown": "content"}
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool(
        api_url="https://fastcrw.com/api",
        api_key="test-key-123",
    )
    tool._run(url="https://example.com")

    mock_make_client.assert_called_once_with("https://fastcrw.com/api", "test-key-123")


@patch("crewai_crw.tools._make_client")
def test_scrape_error_handling(mock_make_client):
    from crewai_crw import CrwScrapeWebsiteTool
    from crw.exceptions import CrwApiError

    mock_client = MagicMock()
    mock_client.scrape.side_effect = CrwApiError("Page not found")
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool()

    with pytest.raises(CrwApiError, match="Page not found"):
        tool._run(url="https://example.com/404")


@patch("crewai_crw.tools._make_client")
def test_scrape_fallback_to_plaintext(mock_make_client):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_client = MagicMock()
    mock_client.scrape.return_value = {
        "markdown": None,
        "plainText": "Plain text fallback content",
    }
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "Plain text fallback content"


@patch("crewai_crw.tools._make_client")
def test_scrape_fallback_to_html(mock_make_client):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_client = MagicMock()
    mock_client.scrape.return_value = {
        "markdown": None,
        "plainText": None,
        "html": "<h1>Hello</h1>",
    }
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "<h1>Hello</h1>"


@patch("crewai_crw.tools._make_client")
def test_scrape_returns_json_when_no_text(mock_make_client):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_client = MagicMock()
    mock_client.scrape.return_value = {
        "markdown": None,
        "plainText": None,
        "html": None,
        "json": {"title": "Test", "price": "$10"},
    }
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == {"title": "Test", "price": "$10"}


# --- CrwCrawlWebsiteTool Tests ---


@patch("crewai_crw.tools._make_client")
def test_crawl_returns_combined_content(mock_make_client):
    from crewai_crw import CrwCrawlWebsiteTool

    mock_client = MagicMock()
    mock_client.crawl.return_value = [
        {
            "markdown": "# Page 1 content",
            "metadata": {"sourceURL": "https://example.com/page1"},
        },
        {
            "markdown": "# Page 2 content",
            "metadata": {"sourceURL": "https://example.com/page2"},
        },
    ]
    mock_make_client.return_value = mock_client

    tool = CrwCrawlWebsiteTool()
    result = tool._run(url="https://example.com")

    assert "Page 1 content" in result
    assert "Page 2 content" in result
    assert "---" in result
    mock_client.crawl.assert_called_once()


@patch("crewai_crw.tools._make_client")
def test_crawl_passes_config(mock_make_client):
    from crewai_crw import CrwCrawlWebsiteTool

    mock_client = MagicMock()
    mock_client.crawl.return_value = [
        {"markdown": "# Done", "metadata": {"sourceURL": "https://example.com"}},
    ]
    mock_make_client.return_value = mock_client

    tool = CrwCrawlWebsiteTool(
        config={"maxDepth": 3, "maxPages": 20, "formats": ["markdown"]},
        poll_interval=5,
        max_wait=60,
    )
    tool._run(url="https://example.com")

    call_kwargs = mock_client.crawl.call_args
    assert call_kwargs[1]["max_depth"] == 3
    assert call_kwargs[1]["max_pages"] == 20
    assert call_kwargs[1]["poll_interval"] == 5.0
    assert call_kwargs[1]["timeout"] == 60.0


@patch("crewai_crw.tools._make_client")
def test_crawl_timeout(mock_make_client):
    from crewai_crw import CrwCrawlWebsiteTool
    from crw.exceptions import CrwTimeoutError

    mock_client = MagicMock()
    mock_client.crawl.side_effect = CrwTimeoutError("Crawl timed out")
    mock_make_client.return_value = mock_client

    tool = CrwCrawlWebsiteTool(max_wait=4, poll_interval=2)

    with pytest.raises(CrwTimeoutError):
        tool._run(url="https://example.com")


@patch("crewai_crw.tools._make_client")
def test_crawl_failure(mock_make_client):
    from crewai_crw import CrwCrawlWebsiteTool
    from crw.exceptions import CrwError

    mock_client = MagicMock()
    mock_client.crawl.side_effect = CrwError("Crawl failed: unknown")
    mock_make_client.return_value = mock_client

    tool = CrwCrawlWebsiteTool()

    with pytest.raises(CrwError, match="Crawl failed"):
        tool._run(url="https://example.com")


@patch("crewai_crw.tools._make_client")
def test_crawl_empty_result(mock_make_client):
    from crewai_crw import CrwCrawlWebsiteTool

    mock_client = MagicMock()
    mock_client.crawl.return_value = []
    mock_make_client.return_value = mock_client

    tool = CrwCrawlWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "No content found."


# --- CrwMapWebsiteTool Tests ---


@patch("crewai_crw.tools._make_client")
def test_map_returns_urls(mock_make_client):
    from crewai_crw import CrwMapWebsiteTool

    mock_client = MagicMock()
    mock_client.map.return_value = [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/blog",
    ]
    mock_make_client.return_value = mock_client

    tool = CrwMapWebsiteTool()
    result = tool._run(url="https://example.com")

    assert "https://example.com/" in result
    assert "https://example.com/about" in result
    assert "https://example.com/blog" in result
    lines = result.strip().split("\n")
    assert len(lines) == 3


@patch("crewai_crw.tools._make_client")
def test_map_empty_result(mock_make_client):
    from crewai_crw import CrwMapWebsiteTool

    mock_client = MagicMock()
    mock_client.map.return_value = []
    mock_make_client.return_value = mock_client

    tool = CrwMapWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "No links discovered."


@patch("crewai_crw.tools._make_client")
def test_map_error_handling(mock_make_client):
    from crewai_crw import CrwMapWebsiteTool
    from crw.exceptions import CrwApiError

    mock_client = MagicMock()
    mock_client.map.side_effect = CrwApiError("Connection refused")
    mock_make_client.return_value = mock_client

    tool = CrwMapWebsiteTool()

    with pytest.raises(CrwApiError, match="Connection refused"):
        tool._run(url="https://example.com")


# --- CrwSearchWebTool Tests ---


@patch("crewai_crw.tools._make_client")
def test_search_returns_formatted_results(mock_make_client):
    from crewai_crw import CrwSearchWebTool

    mock_client = MagicMock()
    mock_client.search.return_value = [
        {
            "title": "Result 1",
            "url": "https://example.com/1",
            "description": "First result",
            "markdown": "# Page One\n\nDetailed content here.",
        },
        {"title": "Result 2", "url": "https://example.com/2", "description": "Second result"},
    ]
    mock_make_client.return_value = mock_client

    tool = CrwSearchWebTool(api_url="https://fastcrw.com/api", api_key="key")
    result = tool._run(query="test query")

    assert "Result 1" in result
    assert "Result 2" in result
    assert "---" in result
    # Verify page content from markdown field is included
    assert "# Page One" in result
    assert "Detailed content here." in result


@patch("crewai_crw.tools._make_client")
def test_search_empty_results(mock_make_client):
    """Search returning an empty list should produce a 'No results found.' message."""
    from crewai_crw import CrwSearchWebTool

    mock_client = MagicMock()
    mock_client.search.return_value = []
    mock_make_client.return_value = mock_client

    tool = CrwSearchWebTool(api_url="https://fastcrw.com/api", api_key="key")
    result = tool._run(query="nonexistent topic")

    assert result == "No results found."
    mock_client.search.assert_called_once()


# --- Crawl: pages with empty markdown ---


@patch("crewai_crw.tools._make_client")
def test_crawl_pages_with_no_content(mock_make_client):
    """Crawl returning pages where all have empty markdown should yield 'No content found.'."""
    from crewai_crw import CrwCrawlWebsiteTool

    mock_client = MagicMock()
    mock_client.crawl.return_value = [
        {"markdown": "", "metadata": {"sourceURL": "https://example.com/a"}},
        {"markdown": "", "metadata": {"sourceURL": "https://example.com/b"}},
    ]
    mock_make_client.return_value = mock_client

    tool = CrwCrawlWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "No content found."


# --- Client close assertion ---


@patch("crewai_crw.tools._make_client")
def test_client_close(mock_make_client):
    """Verify we can call close() on the underlying client."""
    from crewai_crw import CrwScrapeWebsiteTool

    mock_client = MagicMock()
    mock_make_client.return_value = mock_client

    tool = CrwScrapeWebsiteTool()
    tool._client.close()

    mock_client.close.assert_called_once()


# --- Instantiation Tests ---


@patch("crewai_crw.tools._make_client")
def test_all_tools_instantiate(mock_make_client):
    """Verify all tools can be instantiated with defaults."""
    from crewai_crw import (
        CrwScrapeWebsiteTool,
        CrwCrawlWebsiteTool,
        CrwMapWebsiteTool,
        CrwSearchWebTool,
    )

    mock_make_client.return_value = MagicMock()

    scrape = CrwScrapeWebsiteTool()
    assert scrape.name == "CRW web scrape tool"
    assert scrape.api_url is None

    crawl = CrwCrawlWebsiteTool()
    assert crawl.name == "CRW web crawl tool"
    assert crawl.poll_interval == 2
    assert crawl.max_wait == 300

    map_tool = CrwMapWebsiteTool()
    assert map_tool.name == "CRW website map tool"

    search = CrwSearchWebTool()
    assert search.name == "CRW web search tool"
    assert search.api_url is None


@patch("crewai_crw.tools._make_client")
def test_no_api_key_means_no_auth(mock_make_client):
    """When no api_key is set, it should be None."""
    from crewai_crw import CrwScrapeWebsiteTool

    mock_make_client.return_value = MagicMock()

    tool = CrwScrapeWebsiteTool()
    assert tool.api_key is None
    mock_make_client.assert_called_with(None, None)
