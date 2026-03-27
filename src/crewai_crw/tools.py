"""CRW web scraping tools for CrewAI.

CRW is an open-source web scraper built for AI agents.
Self-hosted (free) or managed cloud at https://fastcrw.com.
"""

from __future__ import annotations

import os
import time
from typing import Any

import requests as http_requests
from crewai.tools import BaseTool, EnvVar
from pydantic import BaseModel, ConfigDict, Field


# --- Scrape Tool ---


class CrwScrapeWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL to scrape")


class CrwScrapeWebsiteTool(BaseTool):
    """Scrape webpages using CRW and return clean markdown content.

    CRW is an open-source web scraper built for AI agents. It can run
    self-hosted (free) or via the managed cloud at fastcrw.com.

    Args:
        api_url: CRW server URL. Default: http://localhost:3000
        api_key: Optional API key (required for fastcrw.com cloud).
        config: Scrape configuration options.

    Configuration options:
        formats (list[str]): Output formats. Default: ["markdown"]
            Options: "markdown", "html", "rawHtml", "plainText", "links", "json"
        only_main_content (bool): Strip nav/footer/sidebar. Default: True
        render_js (bool|None): None=auto, True=force JS, False=HTTP only.
        wait_for (int): ms to wait after JS rendering.
        include_tags (list[str]): CSS selectors to include.
        exclude_tags (list[str]): CSS selectors to exclude.
        css_selector (str): Extract specific CSS selector.
        xpath (str): Extract specific XPath.
        headers (dict): Custom HTTP headers.
        json_schema (dict): JSON Schema for LLM extraction.
        proxy (str): Per-request proxy URL.
        stealth (bool): Enable stealth mode.
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "CRW web scrape tool"
    description: str = (
        "Scrape webpages using CRW and return clean markdown content. "
        "CRW is a fast, open-source web scraper with JS rendering support."
    )
    args_schema: type[BaseModel] = CrwScrapeWebsiteToolSchema
    api_url: str = "http://localhost:3000"
    api_key: str | None = None
    config: dict[str, Any] = Field(
        default_factory=lambda: {
            "formats": ["markdown"],
            "onlyMainContent": True,
        }
    )

    env_vars: list[EnvVar] = Field(
        default_factory=lambda: [
            EnvVar(
                name="CRW_API_URL",
                description="CRW server URL (default: http://localhost:3000)",
                required=False,
                default="http://localhost:3000",
            ),
            EnvVar(
                name="CRW_API_KEY",
                description="API key for CRW (required for fastcrw.com cloud)",
                required=False,
            ),
        ]
    )

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.api_url = api_url or os.getenv("CRW_API_URL", "http://localhost:3000")
        self.api_key = api_key or os.getenv("CRW_API_KEY")

    def _run(self, url: str) -> Any:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"url": url, **self.config}

        response = http_requests.post(
            f"{self.api_url.rstrip('/')}/v1/scrape",
            json=payload,
            headers=headers,
            timeout=120,
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("success"):
            raise RuntimeError(
                f"CRW scrape failed: {result.get('error', 'Unknown error')}"
            )

        data = result["data"]

        if data.get("markdown"):
            return data["markdown"]
        if data.get("plainText"):
            return data["plainText"]
        if data.get("html"):
            return data["html"]
        if data.get("json"):
            return data["json"]
        return data


# --- Crawl Tool ---


class CrwCrawlWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL to crawl")


class CrwCrawlWebsiteTool(BaseTool):
    """Crawl websites using CRW and return content from multiple pages.

    CRW performs async BFS crawling with rate limiting, robots.txt respect,
    and sitemap support. Runs self-hosted (free) or via fastcrw.com cloud.

    Args:
        api_url: CRW server URL. Default: http://localhost:3000
        api_key: Optional API key (required for fastcrw.com cloud).
        config: Crawl configuration options.
        poll_interval: Seconds between status checks. Default: 2
        max_wait: Maximum seconds to wait for crawl completion. Default: 300

    Configuration options:
        max_depth (int): Maximum link-follow depth. Default: 2
        max_pages (int): Maximum pages to scrape. Default: 10
        formats (list[str]): Output formats per page. Default: ["markdown"]
        only_main_content (bool): Strip boilerplate. Default: True
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "CRW web crawl tool"
    description: str = (
        "Crawl websites using CRW and return content from multiple pages. "
        "Useful for gathering information across an entire site."
    )
    args_schema: type[BaseModel] = CrwCrawlWebsiteToolSchema
    api_url: str = "http://localhost:3000"
    api_key: str | None = None
    poll_interval: int = 2
    max_wait: int = 300
    config: dict[str, Any] = Field(
        default_factory=lambda: {
            "maxDepth": 2,
            "maxPages": 10,
            "formats": ["markdown"],
            "onlyMainContent": True,
        }
    )

    env_vars: list[EnvVar] = Field(
        default_factory=lambda: [
            EnvVar(
                name="CRW_API_URL",
                description="CRW server URL (default: http://localhost:3000)",
                required=False,
                default="http://localhost:3000",
            ),
            EnvVar(
                name="CRW_API_KEY",
                description="API key for CRW (required for fastcrw.com cloud)",
                required=False,
            ),
        ]
    )

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.api_url = api_url or os.getenv("CRW_API_URL", "http://localhost:3000")
        self.api_key = api_key or os.getenv("CRW_API_KEY")

    def _get_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _run(self, url: str) -> Any:
        headers = self._get_headers()
        base = self.api_url.rstrip("/")

        payload = {"url": url, **self.config}
        response = http_requests.post(
            f"{base}/v1/crawl",
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("success"):
            raise RuntimeError(
                f"CRW crawl start failed: {result.get('error', 'Unknown error')}"
            )

        job_id = result["id"]

        elapsed = 0
        while elapsed < self.max_wait:
            time.sleep(self.poll_interval)
            elapsed += self.poll_interval

            status_resp = http_requests.get(
                f"{base}/v1/crawl/{job_id}",
                headers=headers,
                timeout=30,
            )
            status_resp.raise_for_status()
            status_data = status_resp.json()

            if status_data["status"] == "completed":
                pages = status_data.get("data", [])
                combined = []
                for page in pages:
                    source = page.get("metadata", {}).get("sourceURL", "unknown")
                    content = page.get("markdown", "")
                    if content:
                        combined.append(f"## Source: {source}\n\n{content}")
                return "\n\n---\n\n".join(combined) if combined else "No content found."

            if status_data["status"] == "failed":
                raise RuntimeError("CRW crawl job failed")

        raise TimeoutError(
            f"CRW crawl did not complete within {self.max_wait} seconds"
        )


# --- Map Tool ---


class CrwMapWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL to discover links from")


class CrwMapWebsiteTool(BaseTool):
    """Discover all URLs on a website using CRW's map endpoint.

    Useful for understanding site structure before targeted scraping.
    Uses sitemap.xml and link discovery to find all pages.

    Args:
        api_url: CRW server URL. Default: http://localhost:3000
        api_key: Optional API key (required for fastcrw.com cloud).
        config: Map configuration options.

    Configuration options:
        max_depth (int): Maximum discovery depth. Default: 2
        use_sitemap (bool): Also read sitemap.xml. Default: True
    """

    model_config = ConfigDict(
        arbitrary_types_allowed=True, validate_assignment=True, frozen=False
    )
    name: str = "CRW website map tool"
    description: str = (
        "Discover all URLs on a website. Useful for understanding site structure "
        "before scraping specific pages."
    )
    args_schema: type[BaseModel] = CrwMapWebsiteToolSchema
    api_url: str = "http://localhost:3000"
    api_key: str | None = None
    config: dict[str, Any] = Field(
        default_factory=lambda: {
            "maxDepth": 2,
            "useSitemap": True,
        }
    )

    env_vars: list[EnvVar] = Field(
        default_factory=lambda: [
            EnvVar(
                name="CRW_API_URL",
                description="CRW server URL (default: http://localhost:3000)",
                required=False,
                default="http://localhost:3000",
            ),
            EnvVar(
                name="CRW_API_KEY",
                description="API key for CRW (required for fastcrw.com cloud)",
                required=False,
            ),
        ]
    )

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.api_url = api_url or os.getenv("CRW_API_URL", "http://localhost:3000")
        self.api_key = api_key or os.getenv("CRW_API_KEY")

    def _run(self, url: str) -> Any:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"url": url, **self.config}

        response = http_requests.post(
            f"{self.api_url.rstrip('/')}/v1/map",
            json=payload,
            headers=headers,
            timeout=60,
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("success"):
            raise RuntimeError(
                f"CRW map failed: {result.get('error', 'Unknown error')}"
            )

        links = result.get("data", {}).get("links", [])
        return "\n".join(links) if links else "No links discovered."
