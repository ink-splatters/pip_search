# pip_search.py
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import httpx

if TYPE_CHECKING:
    from collections.abc import Iterator
from bs4 import BeautifulSoup
from loguru import logger

from .http_client import HTTPClient


class SortBy(StrEnum):
    NAME = "name"
    RELEASED = "released"


@dataclass(frozen=True, slots=True)
class SearchConfig:
    base_url: str = "https://pypi.org"
    search_url: str = "https://pypi.org/search/"
    pages: int = 2
    default_sort: SortBy = SortBy.NAME
    project_url_template: str = "https://pypi.org/project/{name}/"
    timeout_s: float = 30.0


CONFIG = SearchConfig()


@dataclass(frozen=True, slots=True)
class SearchOptions:
    sort_by: SortBy = CONFIG.default_sort
    pages: int = CONFIG.pages


@dataclass(frozen=True, slots=True)
class Package:
    name: str
    version: str
    released_at: datetime
    description: str
    url: str

    def released_date_str(self, fmt: str = "%Y-%m-%d") -> str:
        return self.released_at.strftime(fmt)


class _Sel:
    SNIPPET = 'a[class*="package-snippet"]'
    NAME = 'span[class*="package-snippet__name"]'
    VERSION = 'span[class*="package-snippet__version"]'
    CREATED = 'span[class*="package-snippet__created"] time'
    DESCRIPTION = 'p[class*="package-snippet__description"]'
    PROJECT_VERSION = "h1.package-header__name"


_DEFAULT_HEADERS: dict[str, str] = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def _parse_iso_datetime(value: str) -> datetime:
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    dt = datetime.fromisoformat(v)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt


def _make_client(cfg: SearchConfig) -> httpx.Client:
    """Create HTTPX client with default headers and HTTP/2."""
    return HTTPClient(
        http2=True,
        headers=_DEFAULT_HEADERS,
        timeout=httpx.Timeout(cfg.timeout_s),
    )


def _coerce_opts(opts: SearchOptions | dict | None) -> SearchOptions:
    if opts is None:
        return SearchOptions()
    if isinstance(opts, SearchOptions):
        return opts
    sort_by = opts.get("sort_by") or opts.get("sort") or CONFIG.default_sort
    pages = opts.get("pages") or opts.get("page_size") or CONFIG.pages
    return SearchOptions(sort_by=SortBy(str(sort_by)), pages=int(pages))


def _fetch_project_version(client: httpx.Client, url: str, *, timeout_s: float) -> str:
    resp = client.get(url)
    soup = BeautifulSoup(resp.text, "html.parser")
    h1 = soup.select_one(_Sel.PROJECT_VERSION)
    if not h1:
        return "Unknown"
    text = re.sub(r"\s+", " ", h1.get_text(strip=True))
    parts = text.split()
    return parts[-1] if parts else "Unknown"


def search(
    query: str,
    opts: SearchOptions | dict | None = None,
    *,
    client: httpx.Client | None = None,
    config: SearchConfig = CONFIG,
) -> Iterator[Package]:
    o = _coerce_opts(opts)
    c = client or _make_client(config)

    logger.info("Searching PyPI: query={!r} pages={}", query, o.pages)

    packages: list[Package] = []
    for page in range(1, o.pages + 1):
        resp = c.get(config.search_url, params={"q": query, "page": page})
        soup = BeautifulSoup(resp.text, "html.parser")
        snippets = soup.select(_Sel.SNIPPET)
        logger.debug("Parsed page {}: snippets={}", page, len(snippets))

        for snip in snippets:
            name_el = snip.select_one(_Sel.NAME)
            if not name_el:
                continue
            name = re.sub(r"\s+", " ", name_el.get_text(strip=True))

            href = snip.get("href") or ""
            url = (
                urljoin(config.search_url, str(href))
                if href
                else config.project_url_template.format(name=name)
            )

            version_el = snip.select_one(_Sel.VERSION)
            version = (
                re.sub(r"\s+", " ", version_el.get_text(strip=True))
                if version_el and version_el.get_text(strip=True)
                else ""
            )

            created_el = snip.select_one(_Sel.CREATED)
            released_raw = created_el.get("datetime") if created_el else None
            if not released_raw:
                continue
            released_at = _parse_iso_datetime(str(released_raw))

            desc_el = snip.select_one(_Sel.DESCRIPTION)
            description = re.sub(r"\s+", " ", desc_el.get_text(strip=True)) if desc_el else ""

            if not version:
                version = _fetch_project_version(c, url, timeout_s=config.timeout_s)

            packages.append(
                Package(
                    name=name,
                    version=version,
                    released_at=released_at,
                    description=description,
                    url=url,
                )
            )

    match o.sort_by:
        case SortBy.NAME:
            packages.sort(key=lambda p: p.name.casefold())
        case SortBy.RELEASED:
            packages.sort(key=lambda p: p.released_at)

    yield from packages
