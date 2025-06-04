<details>
<summary>[EN] Website Clustering and Analysis Tool</summary>
# Website Clustering and Analysis Tool

#### The purpose of this project is to discover websites with the same templates among a list of URLs or subdomains.

This tool clusters and analyzes websites based on their CSS files. It asynchronously downloads website content, extracts CSS file names, calculates the Jaccard similarity between sites, and groups similar sites into clusters. Additionally, it supports filtering websites based on finding a keyword in the page title or entire HTML content.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Usage](#basic-usage)
  - [Examples](#examples)
- [Arguments](#arguments)
- [Output](#output)
- [Logging](#logging)
- [License](#license)

## Features

- **CSS-Based Clustering**: Extracts CSS files from websites and clusters them based on Jaccard similarity.
- **Keyword Filtering**: Filters websites based on a keyword found in the title or HTML content.
- **Subdomain Discovery**: Queries the subdomains of a target domain using `subfinder`.
- **Real-Time Progress Display**: Shows real-time progress and clustering results in the terminal.
- **JSON Output**: Saves clustering results in a `clusters.json` file for analysis.

## Requirements

- **Python 3.7+**
- **Subfinder**: Required when using the `-d` or `--domain` option.  
  You can install it from [ProjectDiscovery/subfinder](https://github.com/projectdiscovery/subfinder).


## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yunusornek/SiteCluster.git
   cd website-clustering-tool
   ```

2. **Create a Virtual Environment (Optional)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows: `venv\Scripts\activate`
   ```

3. **Install the Required Packages**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```bash
python main.py -dl urls.txt
```


</details>

<details>
<summary>[TR] Web Sitesi Kümeleme ve Analiz Aracı</summary>
# Web Sitesi Kümeleme ve Analiz Aracı

#### Bu projenin amacı bir url listsi veya subdomainler arasındaki aynı template sahip websitelerini keşfetmektir.

Bu araç, web sitelerini CSS dosyalarını kullanarak kümeler ve analiz eder. Web sitesi içeriklerini asenkron olarak indirir, CSS dosya isimlerini çıkarır, siteler arasındaki Jaccard benzerliğini hesaplar ve benzer siteleri kümeler halinde gruplandırır. Ayrıca, bir anahtar kelimeyi sayfa başlığında veya tüm HTML içeriğinde bulmaya dayalı olarak siteleri filtreleme desteği sunar.

## İçindekiler

- [Özellikler](#özellikler)
- [Gereksinimler](#gereksinimler)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
  - [Temel Kullanım](#temel-kullanım)
  - [Örnekler](#örnekler)
- [Argümanlar](#argümanlar)
- [Çıktı](#çıktı)
- [Loglama](#loglama)
- [Lisans](#lisans)

## Özellikler

- **CSS Tabanlı Kümeleme**: Web sitelerinden CSS dosyalarını çıkarır ve Jaccard benzerliğine göre kümeler.
- **Anahtar Kelime Filtreleme**: Web sitelerini başlık veya HTML içeriğinde bir anahtar kelimeye göre filtreler.
- **Alt Alan Adı Bulma**: `subfinder` kullanarak bir hedef alan adının alt alan adlarını sorgular.
- **Gerçek Zamanlı İlerleme Gösterimi**: Terminal'de anlık olarak ilerleme durumu ve kümeleme sonuçlarını gösterir.
- **JSON Çıktısı**: Kümeleme sonuçlarını analiz için `clusters.json` dosyasına kaydeder.

## Gereksinimler

- **Python 3.7+**
- **Subfinder**: `-d` veya `--domain` seçeneği kullanıldığında gereklidir. 
- [ProjectDiscovery/subfinder](https://github.com/projectdiscovery/subfinder) adresinden kurabilirsiniz.

## Kurulum

1. **Depoyu Klonlayın**

   ```bash
   git clone https://github.com/yunusornek/SiteCluster.git
   cd website-clustering-tool
   ```

2. **Sanal Ortam Oluşturun (İsteğe Bağlı)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows için: `venv\Scripts\activate`
   ```

3. **Gerekli Paketleri Yükleyin**

   ```bash
   pip install -r requirements.txt
   ```

   

## Kullanım

### Temel Kullanım

```bash
python main.py -dl urls.txt
```

### Örnekler

- **Varsayılan ayarlarla web sitelerini kümeler**

  ```bash
  python main.py -dl urls.txt
  ```

- **Bir alan adının alt alan adlarını kümeler**

  ```bash
  python main.py -d example.com
  ```

- **Eşzamanlılık değerini 20 iş parçacığı olarak ayarlayın**

  ```bash
  python main.py -dl urls.txt -t 20
  ```

- **Benzerlik eşik değerini 0.6 olarak ayarlayın**

  ```bash
  python main.py -dl urls.txt -th 0.6
  ```

- **Başlıkta "ankara" kelimesini içeren siteleri filtreleyin**

  ```bash
  python main.py -dl urls.txt -f "ankara" -T
  ```

- **HTML içeriğinde "ankara" kelimesini içeren siteleri filtreleyin**

  ```bash
  python main.py -dl urls.txt -f "ankara" -H
  ```

- **İstek zaman aşımını 15 saniye olarak ayarlayın**

  ```bash
  python main.py -dl urls.txt -to 15
  ```

## Argümanlar

- **`-dl`, `--domain-list`**: URL listesinin bulunduğu dosya yolu (örneğin, `urls.txt`). `-d` ile karşılıklı dışlayıcıdır.
- **`-d`, `--domain`**: Hedef alan adının alt alan adlarını bulur (örneğin, `example.com`). `-dl` ile karşılıklı dışlayıcıdır.
- **`-t`, `--threads`**: Eşzamanlı istek sayısı (varsayılan: `10`).
- **`-th`, `--threshold`**: Kümeleme için benzerlik eşiği (varsayılan: `0.5`). Aralık: `0` ile `1` arasında olmalıdır.
- **`-f`, `--filter-word`**: Web sitelerini filtrelemek için anahtar kelime (örneğin, `"erzurum"`).
- **`-T`, `--title`**: Anahtar kelimeyi sayfa başlığında arar. `-f` ile kullanılır.
- **`-H`, `--html`**: Anahtar kelimeyi HTML içeriğinde arar. `-f` ile kullanılır.
- **`-to`, `--timeout`**: İstek zaman aşımı süresi (varsayılan: `10` saniye).

## Çıktı

- **Konsol Görünümü**: İlerleme durumu, işlenen URL sayısı, canlı alan adları, kümeler ve filtrelenmiş kümeler anlık olarak gösterilir.

- **`clusters.json`**: Kümeleme verilerini içeren JSON dosyası.

  ```json
  {
    "clusters": [
      ["https://example.com", "https://example.org"],
      ["https://another-example.com"]
    ],
    "filtered_clusters": [
      ["https://filtered-example.com"]
    ]
  }
  ```

- **`error.log`**: Hata mesajlarını ve hata ayıklama bilgilerini içeren log dosyası.

## Loglama

Araç, önemli olayları ve hataları `error.log` dosyasına kaydeder.
</details>