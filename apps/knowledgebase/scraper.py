"""
Website Scraper Service: Crawls Brightside Car Wash website, extracts content,
and automatically updates the Knowledge Base with chunked vector embeddings.
"""
import logging
import urllib.request
import urllib.parse
from urllib.error import URLError
from django.utils import timezone
from bs4 import BeautifulSoup

from .services import KnowledgeBaseService

logger = logging.getLogger("brightside")

TARGET_WEBSITE_URL = "https://bright-carwash-website.vercel.app/"
KB_DOCUMENT_TITLE = "Brightside Website Knowledge Base"
KB_FILENAME = "brightside_website_kb.txt"


class WebsiteScraperService:
    def __init__(self, target_url: str = TARGET_WEBSITE_URL):
        self.target_url = target_url
        self.kb_service = KnowledgeBaseService()

    def _fetch_url_content(self, url: str) -> str:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as res:
            return res.read().decode("utf-8", errors="ignore")

    def extract_page_text(self, html: str, page_url: str) -> str:
        soup = BeautifulSoup(html, "html.parser")

        # Remove scripts, styles, head, noscript, svg
        for element in soup(["script", "style", "head", "noscript", "svg"]):
            element.decompose()

        lines = []
        parsed_url = urllib.parse.urlparse(page_url)
        page_path = parsed_url.path or "/"
        lines.append(f"=== PAGE: {page_path} ({page_url}) ===")

        for main_tag in soup.find_all(["h1", "h2", "h3", "h4", "p", "li", "span", "div"]):
            text = main_tag.get_text(separator=" ", strip=True)
            if text and len(text) > 10:
                lines.append(text)

        # Deduplicate consecutive identical lines
        cleaned_lines = []
        for line in lines:
            if not cleaned_lines or cleaned_lines[-1] != line:
                cleaned_lines.append(line)

        return "\n".join(cleaned_lines)

    def scrape_and_update_kb(self) -> dict:
        """
        Scrapes the website, extracts knowledge, and updates/overwrites
        the Knowledge Base entry with new embeddings.
        """
        logger.info("Starting website scrape for URL: %s", self.target_url)
        all_content_blocks = [
            f"# Brightside Car Wash Official Website Knowledge\n"
            f"Source URL: {self.target_url}\n"
            f"Scraped At: {timezone.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        ]

        # Crawl target main page and discovered internal links
        visited_urls = set()
        to_visit = [self.target_url]

        while to_visit and len(visited_urls) < 15:
            current_url = to_visit.pop(0)
            if current_url in visited_urls:
                continue
            visited_urls.add(current_url)

            try:
                logger.info("Scraping page: %s", current_url)
                html = self._fetch_url_content(current_url)
                page_text = self.extract_page_text(html, current_url)
                all_content_blocks.append(page_text)

                # Find internal links on bright-carwash-website.vercel.app
                soup = BeautifulSoup(html, "html.parser")
                for link in soup.find_all("a", href=True):
                    href = link['href']
                    full_url = urllib.parse.urljoin(current_url, href)
                    parsed_target = urllib.parse.urlparse(full_url)
                    # Strip fragment to avoid duplicate pages
                    clean_target_url = urllib.parse.urlunparse(parsed_target._replace(fragment=""))
                    parsed_base = urllib.parse.urlparse(self.target_url)

                    if parsed_target.netloc == parsed_base.netloc and clean_target_url not in visited_urls:
                        if not any(clean_target_url.endswith(ext) for ext in [".png", ".jpg", ".pdf", ".css", ".js"]):
                            to_visit.append(clean_target_url)

            except Exception as exc:
                logger.warning("Failed to scrape page '%s': %s", current_url, exc)

        full_knowledge_text = "\n\n".join(all_content_blocks)
        logger.info("Scraped total %d characters from %d pages.", len(full_knowledge_text), len(visited_urls))

        # Ingest into Knowledge Base (replaces old file & generates new embeddings)
        kb_file = self.kb_service.process_raw_text(
            title=KB_DOCUMENT_TITLE,
            filename=KB_FILENAME,
            content_text=full_knowledge_text
        )

        return {
            "kb_file_id": kb_file.id,
            "title": kb_file.title,
            "pages_scraped": len(visited_urls),
            "total_chars": len(full_knowledge_text),
            "updated_at": timezone.now().isoformat()
        }
