# crewai-crw

[![PyPI version](https://img.shields.io/pypi/v/crewai-crw)](https://pypi.org/project/crewai-crw/)
[![Python](https://img.shields.io/pypi/pyversions/crewai-crw)](https://pypi.org/project/crewai-crw/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

CRW web scraping tools for [CrewAI](https://github.com/crewAIInc/crewAI) — scrape, crawl, map, and search the web with AI agents.

[CRW](https://github.com/us/crw) is an open-source web scraper built for AI agents. Single Rust binary, ~6 MB idle RAM, Firecrawl-compatible API.

## Installation

```bash
pip install crewai crewai-crw
# or
uv add crewai crewai-crw
```

That's it. No server to install, no `cargo install`, no Docker. The `crw` SDK automatically downloads and manages the CRW binary for you.

## Quick Start — Zero Config (Subprocess Mode)

```python
from crewai_crw import CrwScrapeWebsiteTool

# Just works — crw SDK handles everything locally
scrape_tool = CrwScrapeWebsiteTool()
```

## Cloud Mode ([fastcrw.com](https://fastcrw.com))

No local binary needed. [Sign up at fastcrw.com](https://fastcrw.com) and get **500 free credits**:

```python
from crewai_crw import CrwScrapeWebsiteTool

scrape_tool = CrwScrapeWebsiteTool(
    api_url="https://fastcrw.com/api",
    api_key="crw_live_...",  # or set CRW_API_KEY env var
)
```

## Advanced: Self-hosted Server

If you prefer running a persistent CRW server (e.g., shared across services):

```bash
# Option A: Install binary
curl -fsSL https://raw.githubusercontent.com/us/crw/main/install.sh | sh
crw  # starts on http://localhost:3000

# Option B: Docker
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
| `CrwSearchWebTool` | Search the web and get results (cloud only) |

## CrewAI Example

```python
from crewai import Agent, Task, Crew
from crewai_crw import CrwScrapeWebsiteTool

# Zero config — just works out of the box
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

### Search the web (Cloud Only)

> **Note:** Web search is a cloud-only feature. It requires `api_url` pointing to a CRW cloud instance (e.g. fastcrw.com). Subprocess mode is not supported for search.

```python
from crewai_crw import CrwSearchWebTool

search_tool = CrwSearchWebTool(
    api_url="https://fastcrw.com/api",
    api_key="YOUR_KEY",
)

# Use in an agent
researcher = Agent(
    role="Web Researcher",
    goal="Find the latest information on any topic",
    backstory="Expert at searching the web for relevant information",
    tools=[search_tool],
)
```

## Configuration

### Constructor Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `api_url` | `str \| None` | `None` | CRW server URL. If unset, uses subprocess mode (no server needed) |
| `api_key` | `str \| None` | `None` | API key (required for fastcrw.com) |
| `config` | `dict` | varies per tool | Tool-specific configuration |

### Environment Variables

Pass `api_url` and `api_key` explicitly when creating tools:

```bash
export CRW_API_URL=https://fastcrw.com/api  # or http://localhost:3000
export CRW_API_KEY=your_api_key              # required for cloud, optional for self-hosted
```

```python
import os

tool = CrwScrapeWebsiteTool(
    api_url=os.getenv("CRW_API_URL"),
    api_key=os.getenv("CRW_API_KEY"),
)
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

### Search Config (Cloud Only)

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `limit` | `int` | `5` | Maximum number of results to return |

## Compared to Firecrawl Tools

| Feature | crewai-crw | Firecrawl Tools |
|---------|-----------|-----------------|
| Requires SDK package | No (uses `crw` SDK, auto-manages binary) | Yes (`firecrawl-py`) |
| Requires API key | No (subprocess or self-hosted) | Yes (always) |
| Server required | No (`pip install` is all you need) | Yes (always) |
| Self-hosted option | Yes (single binary, auto-managed) | Complex (5+ containers) |
| Cloud option | Yes (fastcrw.com) | Yes (firecrawl.dev) |
| Idle RAM | ~6 MB | ~500 MB+ |

## License

MIT
