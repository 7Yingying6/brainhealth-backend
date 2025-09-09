import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.conf import settings
from news_scraper.models import Article
import time
from datetime import datetime

class Command(BaseCommand):
    help = 'Scrapes news articles from Australian news outlets based on keywords'
    
    # Configuration
    SEED_URLS = [
        'https://www.abc.net.au/news/',
        'https://www.smh.com.au/',
        'https://www.theage.com.au/',
        'https://www.afr.com/',
        'https://www.sbs.com.au/news/',
    ]
    
    KEYWORDS = [
        'vitamin d', 'vitamin d deficiency', 'brain health', 'cognitive function',
    'dementia', 'alzheimer', 'depression', 'mental health', 'sunlight',
    'cognitive decline', 'brain fog', 'memory loss', 'omega-3', 'brain benefits',
    'mental clarity', 'seasonal affective', 'neurodegenerative', 'brain function',
    'psychological health', 'health research'
    ]
    
    USER_AGENT = "NewsScraper/1.0 (+http://example.com/bot)"
    REQUEST_DELAY = 2  # Be polite to servers
    MAX_ARTICLES_PER_SITE = 20

    def handle(self, *args, **options):
        # security guard: disabled unless ALLOW_SCRAPER=1
        if not getattr(settings, "ALLOW_SCRAPER", False):
            raise CommandError(
                "Scraper is disabled. Set ALLOW_SCRAPER=1 to enable (local only)."
            )

        self.stdout.write(f"🚀 Starting news scraping at {datetime.now()}")
        self.stdout.write(f"🔍 Keywords: {', '.join(self.KEYWORDS)}")
        
        existing_urls = set(Article.objects.values_list('url', flat=True))
        new_articles = []
        
        for seed_url in self.SEED_URLS:
            try:
                self.stdout.write(f"\n📰 Scraping: {seed_url}")
                articles = self.scrape_site(seed_url, existing_urls)
                new_articles.extend(articles)
                time.sleep(self.REQUEST_DELAY)
            except Exception as e:
                self.stderr.write(f"❌ Error scraping {seed_url}: {e}")
        
        if new_articles:
            try:
                with transaction.atomic():
                    Article.objects.bulk_create(new_articles, ignore_conflicts=True)
                self.stdout.write(self.style.SUCCESS(
                    f"✅ Successfully added {len(new_articles)} new articles!"
                ))
            except Exception as e:
                self.stderr.write(f"❌ Database error: {e}")
        else:
            self.stdout.write("ℹ️ No new articles found.")

    def scrape_site(self, url, existing_urls):
        html = self.fetch_page(url)
        if not html:
            return []
            
        article_links = self.extract_article_links(html, url)
        new_articles = []
        
        for article_url in article_links[:self.MAX_ARTICLES_PER_SITE]:
            if article_url not in existing_urls:
                article_data = self.scrape_article(article_url)
                if article_data and self.contains_keywords(article_data['content']):
                    article = Article(
                        url=article_url,
                        title=article_data['title'],
                        source_domain=urlparse(article_url).netloc,
                        content=article_data['content'],
                        has_keywords=True,
                        keywords_found=self.get_found_keywords(article_data['content'])
                    )
                    new_articles.append(article)
                    existing_urls.add(article_url)
                    self.stdout.write(f"   ✅ Found: {article_data['title'][:50]}...")
        
        return new_articles

    def fetch_page(self, url):
        try:
            headers = {'User-Agent': self.USER_AGENT}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self.stderr.write(f"   ❌ Failed to fetch {url}: {e}")
            return None

    def extract_article_links(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        
        # Common patterns for news article links
        selectors = [
            'a[href*="/article/"]',
            'a[href*="/news/"]',
            'a[href*="/story/"]',
            'article a',
            '.headline a',
            '.article-title a',
            'h2 a',
            'h3 a',
        ]
        
        for selector in selectors:
            for a_tag in soup.select(selector):
                href = a_tag.get('href')
                if href:
                    absolute_url = urljoin(base_url, href)
                    if self.is_article_url(absolute_url):
                        links.add(absolute_url)
        
        return list(links)

    def is_article_url(self, url):
        path = urlparse(url).path
        return any(keyword in path for keyword in ['/article/', '/news/', '/story/'])

    def scrape_article(self, url):
        html = self.fetch_page(url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract title
        title = soup.find('h1')
        title = title.get_text(strip=True) if title else "No Title"
        
        # Extract content - this will vary by site
        content = ""
        content_selectors = [
            'article',
            '.article-body',
            '.story-content',
            '.post-content',
            '[itemprop="articleBody"]',
        ]
        
        for selector in content_selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(strip=True)
                break
        
        return {'title': title, 'content': content}

    def contains_keywords(self, text):
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.KEYWORDS)

    def get_found_keywords(self, text):
        text_lower = text.lower()
        found = [keyword for keyword in self.KEYWORDS if keyword.lower() in text_lower]
        return ', '.join(found)