# crewai-crw

CRW web scraping tools for [CrewAI](https://github.com/crewAIInc/crewAI) — scrape, crawl, and map websites with AI agents.

[CRW](https://github.com/crw-project/crw) is an open-source web scraper built for AI agents. Single Rust binary, ~6 MB idle RAM, Firecrawl-compatible API.

## Installation

```bash
pip install crewai-crw
```

You also need a running CRW instance:

```bash
# Self-hosted (free)
curl -fsSL https://raw.githubusercontent.com/crw-project/crw/main/install.sh | bash
crw  # starts on http://localhost:3000

# Or use the managed cloud at https://fastcrw.com
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

# Self-hosted (default: localhost:3000)
scrape_tool = CrwScrapeWebsiteTool()

# Or use the cloud
scrape_tool = CrwScrapeWebsiteTool(
    api_url="https://fastcrw.com/api",
    api_key="YOUR_KEY",
)

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
```

### Discover all URLs on a site

```python
from crewai_crw import CrwMapWebsiteTool

map_tool = CrwMapWebsiteTool()
```

## Configuration

### Constructor Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `api_url` | `str` | `http://localhost:3000` | CRW server URL |
| `api_key` | `str \| None` | `None` | API key (required for fastcrw.com) |
| `config` | `dict` | varies per tool | Tool-specific configuration |

### Environment Variables

Both `CRW_API_URL` and `CRW_API_KEY` can be set via environment variables as fallbacks.

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
