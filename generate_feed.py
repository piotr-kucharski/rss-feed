import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import feedgenerator
import datetime

def create_oko_press_rss():
    # Adres strony wyszukiwania artykułów
    url = "https://oko.press/szukaj?q=&type=artykuly&page=1"
    rss_file = "oko_press_rss.xml"
    
    # Konfiguracja Selenium - uruchamiamy Chrome w trybie headless
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=chrome_options)
    
    print(f"Pobieranie zawartości z {url}...")
    driver.get(url)
    time.sleep(5)  # Poczekaj na pełne wyrenderowanie strony
    
    html = driver.page_source
    driver.quit()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # Utwórz kanał RSS
    feed = feedgenerator.Rss201rev2Feed(
        title="RSS dla OKO.press - Artykuły",
        link=url,
        description="Automatycznie wygenerowany kanał RSS dla artykułów ze strony OKO.press",
        language="pl"
    )
    
    articles = soup.select("div.post-card")
    print(f"Znaleziono {len(articles)} potencjalnych artykułów.")
    
    added_links = set()
    article_count = 0
    
    for article in articles:
        try:
            title_element = article.select_one("a.post-card__title")
            if title_element:
                title = title_element.get_text(strip=True)
                link = title_element.get("href", "")
                if not link.startswith("http"):
                    link = "https://oko.press" + link if link.startswith("/") else "https://oko.press/" + link
            else:
                continue
            
            if title and link and len(title) > 5:
                if link in added_links:
                    continue
                added_links.add(link)
                
                description = ""
                excerpt_element = article.find("p")
                if excerpt_element:
                    description = excerpt_element.get_text(strip=True)
                
                pubdate = datetime.datetime.now()
                
                feed.add_item(
                    title=title,
                    link=link,
                    description=description,
                    pubdate=pubdate
                )
                article_count += 1
                
                if article_count >= 15:
                    break
            
        except Exception as e:
            print(f"Błąd podczas przetwarzania artykułu: {e}")
            continue
    
    with open(rss_file, 'w', encoding='utf-8') as f:
        feed.write(f, 'utf-8')
    
    print(f"Kanał RSS został zapisany do pliku {rss_file} z {article_count} artykułami")

# Uruchomienie generatora RSS
create_oko_press_rss()
