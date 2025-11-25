import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time

START_URL = "https://www.sgu.ru/gid-pervokursnika-2025"
BASE_DOMAIN = "sgu.ru"
MAX_DEPTH = 10
MAX_PAGES = 1000
DELAY = 0.5
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

visited = set()
results = []

session = requests.Session()
adapter = requests.adapters.HTTPAdapter(max_retries=3)
session.mount("http://", adapter)
session.mount("https://", adapter)
session.headers.update(HEADERS)


def fetch_html(url):
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    return resp.text


def extract_body_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "form", "aside"]):
        tag.decompose()

    main = soup.select_one("main, .block-system-main-block, .page-content, .content")
    text_source = main if main else soup.body

    if not text_source:
        return ""

    lines = [line.strip() for line in text_source.get_text(separator="\n").split("\n") if line.strip()]
    return " ".join(lines)


def get_internal_links(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "javascript:", "#")):
            continue

        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)

        if BASE_DOMAIN not in parsed.netloc:
            continue

        cleaned = full_url.split("#")[0]

        if any(k in cleaned for k in ["gid-pervokursnika", "node", "pro-sgu", "kto-takoy", "studentu-vsyo-pro-uchyobu", "nauka", "socialnaya-podderzhka", "studencheskaya-zhizn", "dostizheniya-studentov", "student-sgu-v-gorode", "nauchka", "internet-sgu", "sovety-starshikh"]):
            links.add(cleaned)

    return links


def scrape(url, depth=0):
    if len(visited) >= MAX_PAGES or depth > MAX_DEPTH or url in visited:
        return

    visited.add(url)
    print(f"{'  '*depth}→ [{len(visited)}/{MAX_PAGES}] {url}")

    try:
        html = fetch_html(url)
        page_text = extract_body_text(html)
        if page_text.strip():
            results.append({
                "url": url,
                # "depth": depth,
                "content": page_text
            })
    except Exception as e:
        print(f"Ошибка при {url}: {e}")
        return

    links = get_internal_links(html, url)

    for link in links:
        if len(visited) >= MAX_PAGES:
            break
        time.sleep(DELAY)
        scrape(link, depth + 1)


def main():
    print(f"Начинаю обход сайта {START_URL}")
    scrape(START_URL)

    output_file = "data_ssu.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nГотово! Сохранено {len(results)} страниц в {output_file}")


if __name__ == "__main__":
    main()
