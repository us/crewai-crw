"""Unit tests for CRW CrewAI tools with mocked HTTP responses."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


# --- CrwScrapeWebsiteTool Tests ---


@patch("crewai_crw.tools.http_requests")
def test_scrape_returns_markdown(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "markdown": "# Hello World\n\nThis is a test.",
            "metadata": {"title": "Test", "sourceURL": "https://example.com"},
        },
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "# Hello World\n\nThis is a test."
    mock_requests.post.assert_called_once()
    call_kwargs = mock_requests.post.call_args
    assert call_kwargs[1]["json"]["url"] == "https://example.com"


@patch("crewai_crw.tools.http_requests")
def test_scrape_with_custom_config(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"markdown": "content"},
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool(
        config={
            "formats": ["markdown", "html"],
            "onlyMainContent": False,
            "renderJs": True,
        }
    )
    tool._run(url="https://example.com")

    call_kwargs = mock_requests.post.call_args
    payload = call_kwargs[1]["json"]
    assert payload["formats"] == ["markdown", "html"]
    assert payload["onlyMainContent"] is False
    assert payload["renderJs"] is True


@patch("crewai_crw.tools.http_requests")
def test_scrape_with_api_key(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"markdown": "content"},
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool(
        api_url="https://fastcrw.com/api",
        api_key="test-key-123",
    )
    tool._run(url="https://example.com")

    call_kwargs = mock_requests.post.call_args
    assert call_kwargs[1]["headers"]["Authorization"] == "Bearer test-key-123"
    assert "fastcrw.com" in call_kwargs[0][0]


@patch("crewai_crw.tools.http_requests")
def test_scrape_error_handling(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": False,
        "error": "Page not found",
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool()

    with pytest.raises(RuntimeError, match="CRW scrape failed"):
        tool._run(url="https://example.com/404")


@patch("crewai_crw.tools.http_requests")
def test_scrape_http_error(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool
    from requests.exceptions import HTTPError

    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool()

    with pytest.raises(HTTPError):
        tool._run(url="https://example.com")


@patch("crewai_crw.tools.http_requests")
def test_scrape_fallback_to_plaintext(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "markdown": None,
            "plainText": "Plain text fallback content",
        },
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "Plain text fallback content"


@patch("crewai_crw.tools.http_requests")
def test_scrape_fallback_to_html(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "markdown": None,
            "plainText": None,
            "html": "<h1>Hello</h1>",
        },
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "<h1>Hello</h1>"


@patch.dict("os.environ", {"CRW_API_URL": "http://custom:9000", "CRW_API_KEY": "env-key"})
@patch("crewai_crw.tools.http_requests")
def test_scrape_env_var_fallback(mock_requests):
    from crewai_crw import CrwScrapeWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"markdown": "content"},
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwScrapeWebsiteTool()
    tool._run(url="https://example.com")

    call_kwargs = mock_requests.post.call_args
    assert "custom:9000" in call_kwargs[0][0]
    assert call_kwargs[1]["headers"]["Authorization"] == "Bearer env-key"


# --- CrwCrawlWebsiteTool Tests ---


@patch("crewai_crw.tools.time.sleep")
@patch("crewai_crw.tools.http_requests")
def test_crawl_start_and_poll(mock_requests, mock_sleep):
    from crewai_crw import CrwCrawlWebsiteTool

    start_response = MagicMock()
    start_response.json.return_value = {"success": True, "id": "job-123"}
    start_response.raise_for_status = MagicMock()

    status_response = MagicMock()
    status_response.json.return_value = {
        "status": "completed",
        "data": [
            {
                "markdown": "# Page 1 content",
                "metadata": {"sourceURL": "https://example.com/page1"},
            },
            {
                "markdown": "# Page 2 content",
                "metadata": {"sourceURL": "https://example.com/page2"},
            },
        ],
    }
    status_response.raise_for_status = MagicMock()

    mock_requests.post.return_value = start_response
    mock_requests.get.return_value = status_response

    tool = CrwCrawlWebsiteTool()
    result = tool._run(url="https://example.com")

    assert "Page 1 content" in result
    assert "Page 2 content" in result
    assert "---" in result
    mock_requests.post.assert_called_once()
    mock_requests.get.assert_called_once()


@patch("crewai_crw.tools.time.sleep")
@patch("crewai_crw.tools.http_requests")
def test_crawl_polls_until_complete(mock_requests, mock_sleep):
    from crewai_crw import CrwCrawlWebsiteTool

    start_response = MagicMock()
    start_response.json.return_value = {"success": True, "id": "job-456"}
    start_response.raise_for_status = MagicMock()

    scraping_response = MagicMock()
    scraping_response.json.return_value = {"status": "scraping"}
    scraping_response.raise_for_status = MagicMock()

    completed_response = MagicMock()
    completed_response.json.return_value = {
        "status": "completed",
        "data": [
            {
                "markdown": "# Done",
                "metadata": {"sourceURL": "https://example.com"},
            },
        ],
    }
    completed_response.raise_for_status = MagicMock()

    mock_requests.post.return_value = start_response
    mock_requests.get.side_effect = [scraping_response, completed_response]

    tool = CrwCrawlWebsiteTool()
    result = tool._run(url="https://example.com")

    assert "Done" in result
    assert mock_requests.get.call_count == 2


@patch("crewai_crw.tools.time.sleep")
@patch("crewai_crw.tools.http_requests")
def test_crawl_timeout(mock_requests, mock_sleep):
    from crewai_crw import CrwCrawlWebsiteTool

    start_response = MagicMock()
    start_response.json.return_value = {"success": True, "id": "job-789"}
    start_response.raise_for_status = MagicMock()

    scraping_response = MagicMock()
    scraping_response.json.return_value = {"status": "scraping"}
    scraping_response.raise_for_status = MagicMock()

    mock_requests.post.return_value = start_response
    mock_requests.get.return_value = scraping_response

    tool = CrwCrawlWebsiteTool(max_wait=4, poll_interval=2)

    with pytest.raises(TimeoutError, match="did not complete"):
        tool._run(url="https://example.com")


@patch("crewai_crw.tools.time.sleep")
@patch("crewai_crw.tools.http_requests")
def test_crawl_failure(mock_requests, mock_sleep):
    from crewai_crw import CrwCrawlWebsiteTool

    start_response = MagicMock()
    start_response.json.return_value = {"success": True, "id": "job-fail"}
    start_response.raise_for_status = MagicMock()

    failed_response = MagicMock()
    failed_response.json.return_value = {"status": "failed"}
    failed_response.raise_for_status = MagicMock()

    mock_requests.post.return_value = start_response
    mock_requests.get.return_value = failed_response

    tool = CrwCrawlWebsiteTool()

    with pytest.raises(RuntimeError, match="crawl job failed"):
        tool._run(url="https://example.com")


# --- CrwMapWebsiteTool Tests ---


@patch("crewai_crw.tools.http_requests")
def test_map_returns_urls(mock_requests):
    from crewai_crw import CrwMapWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {
            "links": [
                "https://example.com/",
                "https://example.com/about",
                "https://example.com/blog",
            ],
        },
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwMapWebsiteTool()
    result = tool._run(url="https://example.com")

    assert "https://example.com/" in result
    assert "https://example.com/about" in result
    assert "https://example.com/blog" in result
    lines = result.strip().split("\n")
    assert len(lines) == 3


@patch("crewai_crw.tools.http_requests")
def test_map_empty_result(mock_requests):
    from crewai_crw import CrwMapWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": True,
        "data": {"links": []},
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwMapWebsiteTool()
    result = tool._run(url="https://example.com")

    assert result == "No links discovered."


@patch("crewai_crw.tools.http_requests")
def test_map_error_handling(mock_requests):
    from crewai_crw import CrwMapWebsiteTool

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "success": False,
        "error": "Connection refused",
    }
    mock_response.raise_for_status = MagicMock()
    mock_requests.post.return_value = mock_response

    tool = CrwMapWebsiteTool()

    with pytest.raises(RuntimeError, match="CRW map failed"):
        tool._run(url="https://example.com")


# --- Instantiation Tests ---


def test_all_tools_instantiate():
    """Verify all three tools can be instantiated with defaults."""
    from crewai_crw import CrwScrapeWebsiteTool, CrwCrawlWebsiteTool, CrwMapWebsiteTool

    scrape = CrwScrapeWebsiteTool()
    assert scrape.name == "CRW web scrape tool"
    assert scrape.api_url == "https://fastcrw.com/api"

    crawl = CrwCrawlWebsiteTool()
    assert crawl.name == "CRW web crawl tool"
    assert crawl.poll_interval == 2
    assert crawl.max_wait == 300

    map_tool = CrwMapWebsiteTool()
    assert map_tool.name == "CRW website map tool"


def test_no_api_key_means_no_auth_header():
    """When no api_key is set, Authorization header should not be present."""
    from crewai_crw import CrwScrapeWebsiteTool

    tool = CrwScrapeWebsiteTool()
    assert tool.api_key is None
