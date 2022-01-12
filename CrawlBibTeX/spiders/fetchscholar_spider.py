import re
import scrapy
from urllib.parse import urlencode
import requests, time
from scrapy.utils.project import get_project_settings

from CrawlBibTeX.spiders.utils import get_paper_titles
from CrawlBibTeX.items import BibTeXScriptItem


class FetchScholarSpider(scrapy.Spider):
    name = "fetchscholar"
    allowed_domains = ["scholar.google.com", "scholar.googleusercontent.com"]
    start_urls = ["http://scholar.google.com/scholar"]
    titles = get_paper_titles("./papers1.csv")

    def auth_human(self, REFERER=None):
        REFERER = "http://scholar.google.com/scholar" if None else REFERER
        SITE_KEY = "6cLe-wvzkSAAAmAAPBMRTvw0Qo4Muexq9bi0DJwx_mJ-"  # 请替换成自己的SITE_KEY
        API_KEY = "6a1keaof0f4c4c1cc6d5zo360m9555ff7a5a55"
        url = f"https://2captcha.com/in.php?key={API_KEY}&method=userrecaptcha&googlekey={SITE_KEY}&pageurl={REFERER}&json=1"
        try:
            response = requests.get(url)
            # if response.status_code == 200:
            # data = response.json()
            # print("response data:", data)
            # return data.get("data", {}).get("taskId")
        except requests.RequestException as e:
            print("create task failed", e)

    def start_requests(self):
        search_header = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        reqs = list()
        for idx, title in enumerate(self.titles):
            params = {
                "hl": "en",
                "as_sdt": "0,5",
                "q": title,
                "btnG": "",
            }
            proxy_meta = get_project_settings().get("HTTP_PROXY") if get_project_settings().get("USE_PROXY") else {}
            # 通过meta传递paper顺序
            meta_dat = {**{"SeqNum": idx}, **proxy_meta}

            self.auth_human()
            reqs.append(scrapy.Request("{url}?{data}".format(url=self.start_urls[0], data=urlencode(params)), headers=search_header, meta=meta_dat, callback=self.get_paper_divs, dont_filter=True))
            time.sleep(1)
        if len(reqs) < 1:
            print("No search result!")
            # exit(1)
            return
        print(f"=>request search urls:\n")
        for req in reqs:
            print(req)
        return reqs

    def get_paper_divs(self, response):
        reqs = list()
        if "not a robot" in response.text:
            print(f"ERROR!!!You need auth!!!For {self.titles[response.meta['SeqNum']]}")
            return
        paper_divs = response.css("#gs_res_ccl_mid > div")
        for paper_div in paper_divs:
            data_cid = paper_div.xpath("./@data-cid").extract_first()
            new_url = "http://scholar.google.com/scholar?q=info:{data_cid}:scholar.google.com/&output=cite&scirp=1&hl=en".format(data_cid=data_cid)
            reqs.append(scrapy.Request(new_url, meta={"SeqNum": response.meta["SeqNum"]}, callback=self.get_bibtex_urls, dont_filter=True))
        # print("\n=>request papers' urls: ")
        # print(reqs)
        if len(reqs) < 1:
            print(f"ERROR! No results for {self.titles[response.meta['SeqNum']]}")
            return
        return reqs

    def get_bibtex_urls(self, response):
        reqs = list()
        cite_nodes = response.selector.css(".gs_citi")
        for node in cite_nodes:
            if "BibTeX" == node.xpath("string(.)").extract_first():
                bibtex_url = node.xpath("./@href").extract_first()
                bibtex_url = bibtex_url.replace("https", "http")
                reqs.append(scrapy.Request(bibtex_url, meta={"SeqNum": response.meta["SeqNum"]}, callback=self.get_bibtex_contents, dont_filter=True))
        # print("\n=>request bibtex urls: ")
        # print("\n")
        # print(reqs)
        if len(reqs) < 1:
            print("No bibtex!")
            # exit(1)
            return
        return reqs

    def get_bibtex_contents(self, response):
        bibtex_item = BibTeXScriptItem()
        bibtex_item["BibTeX"] = response.text
        # 希望根据titles来排序
        bibtex_item["SeqNum"] = response.meta["SeqNum"]
        # print("\n=> got BibTex: ")
        print(f"\n=> For {self.titles[response.meta['SeqNum']]}")
        print(bibtex_item["BibTeX"])
        return [bibtex_item]
