import asyncio
import aiohttp
from aiohttp import ClientSession, ClientError
from bs4 import BeautifulSoup
import os
import logging
import json
from typing import List, Tuple, Optional
import argparse
import subprocess
from urllib.parse import urlparse
import aiofiles

# ANSI renk kodları
COLOR_RESET = "\033[0m"
COLOR_GREEN = "\033[92m"
COLOR_BLUE = "\033[94m"
COLOR_CYAN = "\033[96m"

# Logging ayarları
import logging

class InfoFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.INFO

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler and set level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.addFilter(InfoFilter())

# Create file handler and set level to ERROR
file_handler = logging.FileHandler('error.log', mode='w', encoding='utf-8')
file_handler.setLevel(logging.ERROR)

# Create formatter and add it to handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Jaccard benzerlik hesaplama fonksiyonu
def calculate_jaccard_similarity(set1: List[str], set2: List[str]) -> float:
    set_a, set_b = set(set1), set(set2)
    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union) if union else 0.0

# URL'nin https ile başlamasını sağlama fonksiyonu
def ensure_https(url: str) -> str:
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    parsed = urlparse(url)
    netloc = parsed.netloc
    path = parsed.path.lstrip('/') 
    normalized = f"{parsed.scheme}://{netloc}/{path}" if path else f"{parsed.scheme}://{netloc}"
    return normalized.rstrip('/')

# URL'den protokolü çıkaran fonksiyon
def strip_protocol(url: str) -> str:
    parsed_url = urlparse(url)
    netloc = parsed_url.netloc if parsed_url.netloc else parsed_url.path
    netloc = netloc.lstrip('/')
    return netloc.rstrip('/').lower()

# Tekrarlanan URL'leri kaldıran fonksiyon
def remove_duplicate_urls(urls: List[str]) -> List[str]:
    normalized_urls = {}
    for url in urls:
        normalized_url = ensure_https(url).rstrip('/')
        if not normalized_url:
            continue
        key = strip_protocol(normalized_url)
        if key in normalized_urls:
            if normalized_url.startswith('https://'):
                normalized_urls[key] = normalized_url
        else:
            normalized_urls[key] = normalized_url
    deduplicated = list(normalized_urls.values())
    logger.info(f"Tekrarlanan URL'ler kaldırıldı. {len(deduplicated)} benzersiz URL kaldı.")
    return deduplicated

# URL'den içerik çeken fonksiyon
async def fetch_content(session: ClientSession, url: str, timeout: int) -> Tuple[Optional[str], Optional[str]]:
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), ssl=False, allow_redirects=True) as response:
            if response.status == 200:
                content = await response.text(encoding='utf-8', errors='replace')
                final_url = str(response.url)
                return content, final_url
            else:
                logger.error(f"Beklenmeyen durum kodu {response.status} - {url}")
    except asyncio.TimeoutError:
        logger.error(f"Zaman aşımı hatası - {url}")
    except ClientError as e:
        logger.error(f"İstemci hatası - {url}: {e}")
    except Exception as e:
        logger.error(f"Beklenmeyen hata - {url}: {e}")
    return None, None

# HTML içeriğinden CSS dosyalarını çıkaran fonksiyon
def extract_css_files(html_content: str) -> List[str]:
    soup = BeautifulSoup(html_content, 'html.parser')
    css_files = []
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href')
        if href:
            css_file = os.path.basename(href.split('?')[0])
            css_files.append(css_file)
    return css_files

# Bir siteyi kümeye ekleyen fonksiyon
def assign_site_to_cluster(site: str, css_files: List[str], clusters: List[List[str]], threshold: float, site_css_map: dict):
    for cluster in clusters:
        representative_site = cluster[0]
        if strip_protocol(site) == strip_protocol(representative_site):
            cluster.append(site)
            return
        similarity = calculate_jaccard_similarity(css_files, site_css_map.get(representative_site, []))
        if similarity >= threshold:
            cluster.append(site)
            return
    clusters.append([site])

# İçerik veya başlıkta filtreleme yapacak fonksiyon
def should_filter(content: str, title: str, filter_keyword: str, filter_scope: str) -> bool:
    if filter_scope == 'title':
        return filter_keyword.lower() in (title or '').lower()
    elif filter_scope == 'html':
        return filter_keyword.lower() in content.lower()
    return False

# İşlem çubuğunu gösterecek fonksiyon
def display_progress_bar(current: int, total: int, bar_length: int = 20):
    percent = current / total if total else 0
    filled_length = int(bar_length * percent)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    percentage = int(percent * 100)
    print(f"    [{bar}] {percentage}%", end='\r')

# Kümeleri gösterecek fonksiyon
def display_clusters(clusters: List[List[str]], filtered_clusters: List[List[str]], processed: int, successful: int, total: int):
    os.system('cls' if os.name == 'nt' else 'clear')
    header = (f"{COLOR_BLUE}Tarama ({processed}/{total}) - Canlı Alan Adları ({successful}/{total}) - "
              f"Kümeler: {len(clusters)} - Filtreli Kümeler: {len(filtered_clusters)}{COLOR_RESET}")
    print(header)
    display_progress_bar(processed, total)
    for i, cluster in enumerate(clusters, 1):
        branch = "└──" if i == len(clusters) else "├──"
        print(f"{branch} {COLOR_CYAN}Küme {i}{COLOR_RESET}:")
        for j, site in enumerate(cluster, 1):
            sub_branch = "└──" if j == len(cluster) else "├──"
            print(f"    {sub_branch} {COLOR_GREEN}{site}{COLOR_RESET}")
    for i, cluster in enumerate(filtered_clusters, 1):
        branch = "└──" if i == len(filtered_clusters) else "├──"
        print(f"{branch} {COLOR_CYAN}Filtreli Küme {i}{COLOR_RESET}:")
        for j, site in enumerate(cluster, 1):
            sub_branch = "└──" if j == len(cluster) else "├──"
            print(f"    {sub_branch} {COLOR_GREEN}{site}{COLOR_RESET}")
    
    print("\n"+header)
    display_progress_bar(processed, total)

# Kümeleri JSON dosyasına kaydeden fonksiyon
def save_clusters_to_json(clusters: List[List[str]], filtered_clusters: List[List[str]], filename: str = 'clusters.json'):
    data = {
        "clusters": sorted(clusters, key=len, reverse=True),
        "filtered_clusters": sorted(filtered_clusters, key=len, reverse=True)
    }
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    logger.info(f"Kümeler {filename} dosyasına kaydedildi.")

# Subfinder çalıştıran fonksiyon
async def run_subfinder(domain: str):
    with open('subdomains.txt', 'w', encoding='utf-8') as f:
        f.write('')
    logger.info("Alt alan adları aranıyor...")
    process = await asyncio.create_subprocess_exec(
        "subfinder", "-d", domain, "-o", "subdomains.txt",
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()
    logger.info(f"{domain} için alt alan adları başarıyla alındı.")

# Semaphore ile URL'den içerik çeken yardımcı fonksiyon
async def fetch_with_semaphore(semaphore: asyncio.Semaphore, session: ClientSession, url: str, timeout: int):
    async with semaphore:
        return await fetch_content(session, url, timeout)

# Web sitelerini işleyen fonksiyon
async def process_sites(file_path: str, concurrency: int, threshold: float,
                        filter_keyword: Optional[str], filter_scope: Optional[str],
                        timeout: int, stop_event: asyncio.Event):
    expanded_path = os.path.expanduser(file_path)
    if not os.path.isfile(expanded_path):
        logger.error(f"Dosya bulunamadı: {expanded_path}")
        return

    try:
        async with aiofiles.open(expanded_path, 'r', encoding='utf-8') as f:
            raw_urls = [line.strip() for line in await f.readlines() if line.strip() and not line.startswith('#')]
    except Exception as e:
        logger.error(f"Dosya okuma hatası {expanded_path}: {e}")
        return

    if not raw_urls:
        logger.error("URL listesi boş veya okunamıyor.")
        return

    deduplicated_urls = remove_duplicate_urls(raw_urls)

    clusters = []
    filtered_clusters = []
    site_css_map = {}
    unique_final_urls = set()

    total_urls = len(deduplicated_urls)
    processed_urls = 0
    successful_clusters = 0
    duplicate_urls = 0
    error_urls = 0

    semaphore = asyncio.Semaphore(concurrency)

    async with ClientSession(connector=aiohttp.TCPConnector(ssl=False, keepalive_timeout=30)) as session:
        tasks = [
            fetch_with_semaphore(semaphore, session, url, timeout)
            for url in deduplicated_urls
        ]

        for task in asyncio.as_completed(tasks):
            if stop_event.is_set():
                break

            try:
                content, final_url = await task
                original_url = deduplicated_urls[processed_urls]

                if content and final_url:
                    normalized_final_url = strip_protocol(final_url)
                    if normalized_final_url in unique_final_urls:
                        duplicate_urls += 1
                    else:
                        unique_final_urls.add(normalized_final_url)
                        css_files = extract_css_files(content)
                        site_css_map[final_url] = css_files

                        soup = BeautifulSoup(content, 'html.parser')
                        title = soup.title.string if soup.title else ""

                        if filter_keyword:
                            if should_filter(content, title, filter_keyword, filter_scope):
                                assign_site_to_cluster(final_url, css_files, filtered_clusters, threshold, site_css_map)
                            else:
                                assign_site_to_cluster(final_url, css_files, clusters, threshold, site_css_map)
                        else:
                            assign_site_to_cluster(final_url, css_files, clusters, threshold, site_css_map)

                        successful_clusters += 1
                else:
                    error_urls += 1

                processed_urls += 1
                display_clusters(clusters, filtered_clusters, processed_urls, successful_clusters, total_urls)

                if processed_urls % 50 == 0:
                    await asyncio.sleep(0.5)  # Küçük bir gecikme, daha iyi UI güncellemesi için

            except Exception as e:
                logger.debug(f"Görev sırasında beklenmeyen hata: {e}")
                break

    print(f"\n{COLOR_GREEN}Kümelendirme tamamlandı.{COLOR_RESET}")
    logger.info(f"Toplam Başarılı Kümeler: {successful_clusters}")
    logger.info(f"Toplam Tekrarlanan URL'ler: {duplicate_urls}")
    logger.info(f"Toplam Hatalar: {error_urls}")

    save_clusters_to_json(clusters, filtered_clusters)

# Ana iş parçacığı
async def main():
    stop_event = asyncio.Event()
    if args.domain:
        await run_subfinder(args.domain)
        input_file = 'subdomains.txt'
    else:
        input_file = args.domain_list

    await process_sites(
        file_path=input_file,
        concurrency=args.threads,
        threshold=args.threshold,
        filter_keyword=args.filter_word,
        filter_scope=filter_scope,
        timeout=args.timeout,
        stop_event=stop_event
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Web sitelerini kümelendirme ve analiz aracı.",
        epilog="Örnek kullanım: python script.py -dl urls.txt -t 20 -th 0.6 -f 'erzurum' -T",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-dl', '--domain-list', type=str, help='URL listesi dosya yolu (örn., urls.txt)')
    group.add_argument('-d', '--domain', type=str, help='Hedef alan adı (örn., example.com)')

    parser.add_argument('-t', '--threads', type=int, default=10, help='Eş zamanlı istek sayısı (varsayılan: 10)')
    parser.add_argument('-th', '--threshold', type=float, default=0.5, help='Benzerlik eşiği (varsayılan: 0.5)')
    parser.add_argument('-f', '--filter-word', type=str, help='Web sitelerini filtrelemek için anahtar kelime (örn., "erzurum")')

    filter_group = parser.add_mutually_exclusive_group()
    filter_group.add_argument('-T', '--title', action='store_true', help='Filtre kelimesini sayfa başlığında ara')
    filter_group.add_argument('-H', '--html', action='store_true', help='Filtre kelimesini HTML içeriğinde ara')

    parser.add_argument('-to', '--timeout', type=int, default=10, help='İstek zaman aşımı süresi (varsayılan: 10 saniye)')

    args = parser.parse_args()

    # Filtre arama alanını belirle
    if args.filter_word:
        if args.title:
            filter_scope = 'title'
        elif args.html:
            filter_scope = 'html'
        else:
            filter_scope = 'title'
    else:
        filter_scope = None

    input_file = args.domain_list if args.domain_list else None

    if args.domain_list and not os.path.isfile(args.domain_list):
        logger.info(f"Dosya bulunamadı: {args.domain_list}")
        exit(1)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt alındı, kapatma başlatılıyor...")
        print(f"\n{COLOR_GREEN}Program başarıyla sonlandırıldı.{COLOR_RESET}")
        exit(0)
