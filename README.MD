## Introduction

**This project is just for fun! Use it with caution!**

This is project about crawling the BibTex on [google scholar](https://scholar.google.com/schhp?hl=en) automatically with paper titles given

## Structure

```text
.
├── bibtex.txt
├── CrawlingBibtex
│   ├── __init__.py
│   ├── items.py
│   ├── middlewares.py
│   ├── pipelines.py
│   ├── settings.py [bibtex save path's configuration]
│   └── spiders
│       ├── fetchscholar_spider.py
│       ├── __init__.py
│       ├── __pycache__
│       └── utils.py
├── main.py
├── papers.csv [papers' titles configuration]
├── README.MD
└── scrapy.cfg
```

## Usage

### Environment

* python: 3.8
* Scrapy: 2.4.1

### Config

each of the papers' titles lays in the papers.csv file as single line, if you want to ignore some line, just comment it by '#'

### Run

just execute follow command

```shell
python main.py
```

**Notice**
you may need to configure the proxy in the settings.py

```python
USE_PROXY = True
HTTP_PROXY = {'proxy': 'http://127.0.0.1:1082'}
```

