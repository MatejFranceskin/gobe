import requests
from bs4 import BeautifulSoup
import json
import time
import re
from urllib.parse import urljoin, urlparse
from collections import deque
import os

class GobeSiteCrawler:
    def __init__(self, base_url="https://www.gobe.si/", search_term="v pripravi"):
        self.base_url = base_url
        self.search_term = search_term.lower()
        self.visited_urls = set()
        self.found_pages = []
        self.all_links = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def is_valid_gobe_url(self, url):
        """Check if URL belongs to the entire gobe.si domain"""
        try:
            # Check for empty or obviously invalid URLs
            if not url or len(url.strip()) == 0:
                return False
                
            # Check for URLs that end with encoded spaces or multiple encoded characters
            if url.endswith('%20') or url.endswith('%20%20'):
                return False
                
            parsed = urlparse(url)
            
            # Check if it's a valid gobe.si URL
            return (parsed.netloc == 'www.gobe.si' and 
                    not parsed.path.endswith(('.jpg', '.jpeg', '.png', '.gif', '.pdf', '.css', '.js', '.ico')) and
                    not 'mailto:' in url and
                    not parsed.path.startswith('/admin') and
                    not parsed.path.startswith('/forum') and
                    not parsed.path.startswith('/slike'))  # Skip admin, forum, and slike sections
        except Exception as e:
            print(f"Error validating URL {url}: {e}")
            return False
    
    def clean_url(self, url):
        """Remove hash fragments, query parameters, and clean up spaces from URL"""
        # First, strip any actual spaces from the URL
        url = url.strip()
        
        # Replace any remaining spaces with %20 for proper URL encoding
        url = url.replace(' ', '%20')
        
        parsed = urlparse(url)
        # Reconstruct URL without fragment (#) and query (?)
        clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Remove trailing %20 (URL-encoded spaces) and slashes
        clean_url = clean_url.rstrip('%20').rstrip('/')
        
        # Add back single slash for root paths
        if not clean_url.endswith('/') and parsed.path == '/':
            clean_url += '/'
            
        return clean_url
    
    def get_page_content(self, url):
        """Fetch page content with error handling"""
        try:
            print(f"Fetching: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def extract_links(self, html_content, base_url):
        """Extract all links from HTML content"""
        links = set()
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                # Clean the URL (remove # and ? parts)
                clean_full_url = self.clean_url(full_url)
                if self.is_valid_gobe_url(clean_full_url):
                    links.add(clean_full_url)
        except Exception as e:
            print(f"Error extracting links: {e}")
        return links
    
    def search_for_term_in_content(self, html_content, url):
        """Search for the term in page content and extract mushroom details"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text_content = soup.get_text().lower()
            
            if self.search_term in text_content:
                # Extract title
                title_tag = soup.find('title')
                title = title_tag.text.strip() if title_tag else "No title"
                
                # Extract meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ''
                
                # Find snippet containing the search term
                snippet = self.extract_snippet(text_content, self.search_term)
                
                # Extract mushroom information from the HTML structure
                latin_name = ""
                slovenian_name = ""
                full_name = ""
                uzitnost = ""
                
                # Look for the h1 tag that contains both names
                h1_tag = soup.find('h1')
                if h1_tag:
                    h1_text = h1_tag.get_text()
                    # Split by comma to get latin and slovenian names
                    if ',' in h1_text:
                        parts = h1_text.split(',', 1)
                        latin_name = parts[0].strip()
                        slovenian_name = parts[1].strip()
                
                # Look for the strong tag that contains the full scientific name
                strong_tag = soup.find('strong')
                if strong_tag:
                    full_name = strong_tag.get_text().strip()
                
                # Extract užitnost information
                uzitnost = self.extract_uzitnost(soup)
                
                page_info = {
                    'url': url,
                    'title': title,
                    'description': description,
                    'snippet': snippet,
                    'latin_name': latin_name,
                    'slovenian_name': slovenian_name,
                    'full_name': full_name,
                    'uzitnost': uzitnost,
                    'found_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.found_pages.append(page_info)
                print(f"✓ FOUND '{self.search_term}' in: {url}")
                print(f"  Title: {title}")
                print(f"  Latin: {latin_name}")
                print(f"  Slovenian: {slovenian_name}")
                print(f"  Full: {full_name}")
                print(f"  Užitnost: {uzitnost}")
                return True
        except Exception as e:
            print(f"Error searching content in {url}: {e}")
        return False
    
    def extract_snippet(self, text, search_term, context_length=200):
        """Extract a snippet around the search term"""
        index = text.find(search_term)
        if index == -1:
            return ""
        
        start = max(0, index - context_length)
        end = min(len(text), index + len(search_term) + context_length)
        snippet = text[start:end].strip()
        
        # Clean up the snippet
        snippet = re.sub(r'\s+', ' ', snippet)
        return snippet
    
    def extract_uzitnost(self, soup):
        """Extract užitnost (edibility) information from page content"""
        uzitnost = ""
        
        # Look for paragraph tags containing usage/toxicity information
        rows = soup.find_all('p')
        for row in rows:
            srow = str(row)
            if "UPORABNOST" in srow or "STRUPENOST" in srow:
                # Clean up HTML tags and formatting
                srow = srow.replace('<p class="vspace">', '').replace('<strong>', '').replace('</strong>', '').replace('</p>', '').replace('<span class="-pm--3">', '').replace('</span>', '').strip()
                srow = srow.replace('UPORABNOST: ', '').replace('STRUPENOST: ', '')
                edibility = srow.lower().strip()
                
                # Normalize the edibility information based on the patterns from webscrape.py
                if edibility.startswith("užitnost neznana"):
                    uzitnost = "užitnost neznana"
                elif edibility.startswith("neznana"):
                    uzitnost = "užitnost neznana"
                elif edibility.startswith("užitnost ni znana"):
                    uzitnost = "užitnost neznana"
                elif edibility.startswith("pogojno užit"):
                    uzitnost = "pogojno užitna"
                elif edibility.startswith("kuhana je užitna"):
                    uzitnost = "pogojno užitna"
                elif edibility.startswith("smrtno strupen"):
                    uzitnost = "smrtno strupena"
                elif edibility.startswith("strupena"):
                    uzitnost = "strupena"
                elif edibility.startswith("strupna"):
                    uzitnost = "strupena"
                elif edibility.startswith("neužitna; vsebuje strupe"):
                    uzitnost = "strupena"
                elif edibility.startswith("neužit"):
                    uzitnost = "neužitna"
                elif edibility.startswith("mlada užitna"):
                    uzitnost = "mlada užitna"
                elif edibility.startswith("mlad je užiten"):
                    uzitnost = "mlada užitna"
                elif edibility.startswith("užiten"):
                    uzitnost = "užitna"
                elif edibility.startswith("užitna"):
                    uzitnost = "užitna"
                elif edibility.startswith("zelo dobra užitna goba"):
                    uzitnost = "užitna"
                elif edibility.startswith("užitni so klobuki"):
                    uzitnost = "užitna"
                elif edibility.startswith("dobra"):
                    uzitnost = "užitna"
                elif edibility.startswith("odlična"):
                    uzitnost = "užitna"
                elif edibility.startswith("sicer užitna"):
                    uzitnost = "užitna"
                elif edibility.startswith("goba je sicer veljala za užitno"):
                    uzitnost = "neužitna"
                elif "vsebuje smrtno nevarno snov" in edibility:
                    uzitnost = "smrtno strupena"
                elif edibility.startswith("ni zelo strupena"):
                    uzitnost = "strupena"
                elif edibility.startswith("opredeljena sicer kot užitna, vendar ker vsebuje halucinogene snovi"):
                    uzitnost = "strupena"
                elif edibility.startswith("surova strupena. šele po dolgotrajnem"):
                    uzitnost = "strupena"
                else:
                    # If we found UPORABNOST/STRUPENOST but couldn't classify it, store the raw text
                    uzitnost = edibility[:100]  # Limit length to avoid very long strings
                
                break  # Stop at first match
        
        return uzitnost
    
    def crawl_systematically(self):
        """Crawl the entire gobe.si site systematically to find all pages"""
        print(f"Starting systematic crawl of entire {self.base_url} domain")
        print(f"Looking for pages containing: '{self.search_term}'")
        print("=" * 60)
        
        # Start with the base URL and common sections (excluding forum)
        urls_to_visit = deque([
            self.base_url,
            f"{self.base_url}Gobe/",
            f"{self.base_url}index.php",
            f"{self.base_url}novice/",
            f"{self.base_url}povezave/",
            f"{self.base_url}vsebina/",
            f"{self.base_url}o-nas/",
            f"{self.base_url}kontakt/"
        ])
        
        # Add letter-based paths for Gobe section (most likely to contain "v pripravi")
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for letter in alphabet:
            letter_url = f"{self.base_url}Gobe/{letter}/"
            urls_to_visit.append(letter_url)
        
        pages_crawled = 0
        queued_urls = set(urls_to_visit)  # Track what's already in queue
        
        while urls_to_visit:
            current_url = urls_to_visit.popleft()
            queued_urls.discard(current_url)  # Remove from queued set
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            pages_crawled += 1
            
            print(f"Crawling ({pages_crawled}) [Queue: {len(urls_to_visit)}]: {current_url}")
            
            # Add delay to be respectful to the server
            time.sleep(0.3)
            
            # Fetch page content
            html_content = self.get_page_content(current_url)
            if not html_content:
                continue
            
            # Search for our term in this page
            self.search_for_term_in_content(html_content, current_url)
            
            # Extract links to discover more pages
            links = self.extract_links(html_content, current_url)
            self.all_links.update(links)
            
            # Add new links to visit queue (only if not visited and not already queued)
            new_links_added = 0
            for link in links:
                if link not in self.visited_urls and link not in queued_urls:
                    urls_to_visit.append(link)
                    queued_urls.add(link)
                    new_links_added += 1
            
            if pages_crawled % 50 == 0:
                print(f"=== Progress Report ===")
                print(f"Pages crawled: {pages_crawled}")
                print(f"Queue size: {len(urls_to_visit)}")
                print(f"Matches found: {len(self.found_pages)}")
                print(f"New URLs added this round: {new_links_added}")
                print(f"=======================")
        
        print(f"\nCrawling completed!")
        print(f"Total pages crawled: {pages_crawled}")
        print(f"Total links discovered: {len(self.all_links)}")
        print(f"Pages containing '{self.search_term}': {len(self.found_pages)}")
    
    def save_results(self, filename='gobe_results.txt'):
        """Save results to semicolon-separated text file"""
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write("URL;LatinName;SlovenianName;FullName;Uzitnost\n")
            # Write data
            for page in self.found_pages:
                url = page.get('url', '')
                latin_name = page.get('latin_name', '')
                slovenian_name = page.get('slovenian_name', '')
                full_name = page.get('full_name', '')
                uzitnost = page.get('uzitnost', '')
                f.write(f"{url};{latin_name};{slovenian_name};{full_name};{uzitnost}\n")
        
        print(f"Results saved to {filename}")
        print(f"Found {len(self.found_pages)} pages containing '{self.search_term}'")
    
    def print_summary(self):
        """Print a summary of findings"""
        print(f"\n{'='*60}")
        print(f"CRAWLING SUMMARY")
        print(f"{'='*60}")
        print(f"Search term: '{self.search_term}'")
        print(f"Base URL: {self.base_url}")
        print(f"Pages crawled: {len(self.visited_urls)}")
        print(f"Links discovered: {len(self.all_links)}")
        print(f"Pages containing '{self.search_term}': {len(self.found_pages)}")
        
        if self.found_pages:
            print(f"\n🔍 PAGES WITH '{self.search_term}':")
            print("=" * 80)
            for i, page in enumerate(self.found_pages, 1):
                print(f"{i:3d}. {page['url']}")
                print(f"     Latin: {page.get('latin_name', 'N/A')}")
                print(f"     Slovenian: {page.get('slovenian_name', 'N/A')}")
                print(f"     Full: {page.get('full_name', 'N/A')}")
                print(f"     Užitnost: {page.get('uzitnost', 'N/A')}")
                print()

def main():
    # Initialize crawler
    crawler = GobeSiteCrawler(
        base_url="https://www.gobe.si/",
        search_term="v pripravi"
    )
    
    try:
        print("🔍 COMPLETE GOBE.SI DOMAIN CRAWLER")
        print("=" * 60)
        print("This tool will systematically crawl the entire gobe.si domain")
        print(f"to find all pages containing '{crawler.search_term}'")
        print()
        
        # Crawl systematically
        crawler.crawl_systematically()
        
        # Print summary
        crawler.print_summary()
        
        # Save results
        crawler.save_results('gobe_v_pripravi_pages.txt')
        
        if crawler.found_pages:
            print(f"\n🎯 SUCCESS: Found {len(crawler.found_pages)} pages containing '{crawler.search_term}'!")
        else:
            print(f"\n❌ No pages containing '{crawler.search_term}' were found.")
        
    except KeyboardInterrupt:
        print("\nCrawling interrupted by user")
        crawler.print_summary()
        crawler.save_results('gobe_partial_results.txt')
    except Exception as e:
        print(f"Error during crawling: {e}")
        crawler.save_results('gobe_error_results.txt')

if __name__ == "__main__":
    main()
