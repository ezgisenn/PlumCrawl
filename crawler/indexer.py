import urllib.request
import urllib.error
from urllib.parse import urljoin, urlparse
from html.parser import HTMLParser
import sqlite3
import threading
import time
import os
import ssl
import gzip

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'plumcrawl.db')

class PlumLinkParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.links = []
        self.text_content = []
        self.ignore_tags = ['script', 'style', 'nav', 'footer', 'header', 'meta']
        self.is_ignored_section = False

    def handle_starttag(self, tag, attrs):
        if tag in self.ignore_tags:
            self.is_ignored_section = True
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    full_url = urljoin(self.base_url, value)
                    if urlparse(full_url).scheme in ['http', 'https']:
                        clean_url = full_url.split('#')[0]
                        if clean_url not in self.links: 
                            self.links.append(clean_url)

    def handle_endtag(self, tag):
        if tag in self.ignore_tags:
            self.is_ignored_section = False

    def handle_data(self, data):
        if not self.is_ignored_section:
            cleaned_data = data.strip()
            if cleaned_data:
                self.text_content.append(cleaned_data)

class PlumIndexer:
    def __init__(self, max_queue_depth=5000, rate_limit_sec=0.1, max_threads=5):
        self.max_queue_depth = max_queue_depth
        self.rate_limit_sec = rate_limit_sec
        self.max_threads = max_threads
        self.is_running = False
        self.db_lock = threading.Lock()

    def get_db_connection(self):
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn

    def _execute_db(self, query, params=()):
        with self.db_lock:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id

    def add_many_to_queue(self, links, depth, parent_url):
        if not links:
            return
        with self.db_lock:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            data = [(url, depth, parent_url) for url in links]
            try:
                cursor.executemany(
                    "INSERT OR IGNORE INTO crawl_queue (url, depth, parent_url, status) VALUES (?, ?, ?, 0)",
                    data
                )
                conn.commit()
            except sqlite3.OperationalError:
                pass
            finally:
                conn.close()

    def add_to_queue(self, url, depth, parent_url):
        self._execute_db(
            "INSERT OR IGNORE INTO crawl_queue (url, depth, parent_url, status) VALUES (?, ?, ?, 0)",
            (url, depth, parent_url)
        )

    def get_next_from_queue(self):
        with self.db_lock:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT url, depth FROM crawl_queue WHERE status = 0 LIMIT 1")
            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE crawl_queue SET status = 1 WHERE url = ?", (row['url'],))
                conn.commit()
            conn.close()
            return row

    def get_current_queue_depth(self):
        with self.db_lock:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM crawl_queue WHERE status = 0")
            count = cursor.fetchone()[0]
            conn.close()
            return count

    def process_url(self, url, depth, max_depth, origin_url, skip_extraction=False):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip',
                'Connection': 'keep-alive'
            }
            req = urllib.request.Request(url, headers=headers)
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with urllib.request.urlopen(req, context=ctx, timeout=5) as response:
                html_bytes = response.read()
                
                if response.info().get('Content-Encoding') == 'gzip':
                    html_bytes = gzip.decompress(html_bytes)
                    
                html_str = html_bytes.decode('utf-8', errors='ignore')
                
            parser = PlumLinkParser(url)
            parser.feed(html_str)
            text_content = " ".join(parser.text_content)
            
            self._execute_db(
                "INSERT OR IGNORE INTO pages (url, origin_url, depth, title, content, raw_html) VALUES (?, ?, ?, ?, ?, ?)",
                (url, origin_url, depth, "Extracted Title", text_content, html_str)
            )
            
            self._execute_db("UPDATE crawl_queue SET status = 2 WHERE url = ?", (url,))
            
            # EĞER BACK PRESSURE AKTİF DEĞİLSE YENİ LİNKLERİ EKLE
            if depth < max_depth and not skip_extraction:
                self.add_many_to_queue(parser.links, depth + 1, url)
                    
        except Exception:
            self._execute_db("UPDATE crawl_queue SET status = 3 WHERE url = ?", (url,))

    def _worker_loop(self, max_depth, origin_url):
        idle_counter = 0
        while self.is_running:
            task = self.get_next_from_queue()

            if not task:
                idle_counter += 1
                if idle_counter > 15: 
                    break
                time.sleep(1)
                continue
                
            idle_counter = 0
            url, depth = task['url'], task['depth']

            current_depth = self.get_current_queue_depth()
            skip_extraction = current_depth > self.max_queue_depth

            self.process_url(url, depth, max_depth, origin_url, skip_extraction)
            time.sleep(self.rate_limit_sec)

    def index(self, origin, k):
        self.is_running = True
        self.add_to_queue(origin, 0, "START")
        
        threads = []
        for i in range(self.max_threads):
            t = threading.Thread(target=self._worker_loop, args=(k, origin), name=f"Worker-{i+1}")
            t.start()
            threads.append(t)
            
        for t in threads:
            t.join()