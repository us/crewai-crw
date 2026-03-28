# crewai-crw

[![PyPI version](https://img.shields.io/pypi/v/crewai-crw)](https://pypi.org/project/crewai-crw/)
[![Python](https://img.shields.io/pypi/pyversions/crewai-crw)](https://pypi.org/project/crewai-crw/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

CRW web scraping tools for [CrewAI](https://github.com/crewAIInc/crewAI) — scrape, crawl, and map websites with AI agents.

[CRW](https://github.com/us/crw) is an open-source web scraper built for AI agents. Single Rust binary, ~6 MB idle RAM, Firecrawl-compatible API.

## Installation

```bash
pip install crewai crewai-crw
# or
uv add crewai crewai-crw
```

## Setup — Pick One

### Option A: Cloud ([fastcrw.com](https://fastcrw.com)) — Quickest Start

No server to install. [Sign up at fastcrw.com](https://fastcrw.com) and get **500 free credits** to start scraping:

```bash
export CRW_API_KEY=crw_live_...  # get yours at fastcrw.com
```

```python
from crewai_crw import CrwScrapeWebsiteTool

# Cloud is the default — just set CRW_API_KEY and go
scrape_tool = CrwScrapeWebsiteTool()
```

### Option B: Self-hosted with binary (free, no limits)

Single binary, ~15 MB download, ~6 MB idle RAM. No Docker needed.

```bash
curl -fsSL https://raw.githubusercontent.com/us/crw/main/install.sh | bash
crw  # starts on http://localhost:3000
```

```python
from crewai_crw import CrwScrapeWebsiteTool

scrape_tool = CrwScrapeWebsiteTool(api_url="http://localhost:3000")
```

### Option C: Self-hosted with Docker

```bash
docker run -d -p 3000:3000 ghcr.io/us/crw:latest
```

```python
scrape_tool = CrwScrapeWebsiteTool(api_url="http://localhost:3000")
```

## Tools

| Tool | Description |
|------|-------------|
| `CrwScrapeWebsiteTool` | Scrape a single URL and get clean markdown |
| `CrwCrawlWebsiteTool` | BFS crawl a website, collect content from multiple pages |
| `CrwMapWebsiteTool` | Discover all URLs on a website |

## Quick Start

```python
from crewai import Agent, Task, Crew
from crewai_crw import CrwScrapeWebsiteTool

# Self-hosted: no args needed (connects to localhost:3000)
# Cloud: CrwScrapeWebsiteTool(api_url="https://fastcrw.com/api", api_key="crw_live_...")
scrape_tool = CrwScrapeWebsiteTool()

researcher = Agent(
    role="Web Researcher",
    goal="Research and summarize information from websites",
    backstory="Expert at extracting key information from web pages",
    tools=[scrape_tool],
)

task = Task(
    description="Scrape https://example.com and summarize the content",
    expected_output="A summary of the page content",
    agent=researcher,
)

crew = Crew(agents=[researcher], tasks=[task])
result = crew.kickoff()
```

### Crawl an entire site

```python
from crewai_crw import CrwCrawlWebsiteTool

crawl_tool = CrwCrawlWebsiteTool(
    config={
        "maxDepth": 3,
        "maxPages": 50,
        "formats": ["markdown"],
        "onlyMainContent": True,
    }
)

# Use in an agent
researcher = Agent(
    role="Deep Researcher",
    goal="Crawl documentation sites and extract comprehensive information",
    backstory="Expert at gathering information across multiple pages",
    tools=[crawl_tool],
)
```

### Discover all URLs on a site

```python
from crewai_crw import CrwMapWebsiteTool

map_tool = CrwMapWebsiteTool()

# Use in an agent
mapper = Agent(
    role="Site Mapper",
    goal="Discover and catalog all pages on a website",
    backstory="Expert at understanding website structure",
    tools=[map_tool],
)
```

## Configuration

### Constructor Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `api_url` | `str` | `http://localhost:3000` | CRW server URL |
| `api_key` | `str \| None` | `None` | API key (required for fastcrw.com) |
| `config` | `dict` | varies per tool | Tool-specific configuration |

### Environment Variables

Both `CRW_API_URL` and `CRW_API_KEY` can be set via environment variables as fallbacks:

```bash
export CRW_API_URL=https://fastcrw.com/api  # or http://localhost:3000
export CRW_API_KEY=your_api_key              # required for cloud, optional for self-hosted
```

```python
# With env vars set, no constructor args needed:
tool = CrwScrapeWebsiteTool()
```

### Scrape Config

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `formats` | `list[str]` | `["markdown"]` | Output formats: markdown, html, rawHtml, plainText, links, json |
| `onlyMainContent` | `bool` | `true` | Strip nav/footer/sidebar |
| `renderJs` | `bool\|null` | `null` | null=auto, true=force JS, false=HTTP only |
| `waitFor` | `int` | — | ms to wait after JS rendering |
| `includeTags` | `list[str]` | `[]` | CSS selectors to include |
| `excludeTags` | `list[str]` | `[]` | CSS selectors to exclude |

### Crawl Config

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `maxDepth` | `int` | `2` | Maximum link-follow depth |
| `maxPages` | `int` | `10` | Maximum pages to scrape |
| `formats` | `list[str]` | `["markdown"]` | Output formats per page |
| `onlyMainContent` | `bool` | `true` | Strip boilerplate |

### Map Config

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `maxDepth` | `int` | `2` | Maximum discovery depth |
| `useSitemap` | `bool` | `true` | Also read sitemap.xml |

## Compared to Firecrawl Tools

| Feature | crewai-crw | Firecrawl Tools |
|---------|-----------|-----------------|
| Requires SDK package | No (uses `requests`) | Yes (`firecrawl-py`) |
| Requires API key | No (self-hosted) | Yes (always) |
| Self-hosted option | Yes (single binary) | Complex (5+ containers) |
| Cloud option | Yes (fastcrw.com) | Yes (firecrawl.dev) |
| Idle RAM | ~6 MB | ~500 MB+ |

## License

MIT
