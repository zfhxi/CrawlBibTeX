import scrapy
from urllib.parse import urlencode
from scrapy.utils.project import get_project_settings

from CrawlBibTeX.spiders.utils import get_paper_titles
from CrawlBibTeX.items import BibTeXScriptItem


class FetchScholarSpider(scrapy.Spider):
    name = 'fetchscholar'
    allowed_domains = ['scholar.google.com', 'scholar.googleusercontent.com']
    start_urls = ['http://scholar.google.com/scholar']
    titles = get_paper_titles('./papers.csv')

    def start_requests(self):
        search_header = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        reqs = list()
        for idx, title in enumerate(self.titles):
            params = {
                'hl': 'en',
                'as_sdt': '0,5',
                'q': title,
                'btnG': '',
            }
            proxy_meta = get_project_settings().get('HTTP_PROXY') if get_project_settings().get('USE_PROXY') else {}
            # 通过meta传递paper顺序
            meta_dat = {**{'SeqNum': idx}, **proxy_meta}
            reqs.append(
                scrapy.Request('{url}?{data}'.format(url=self.start_urls[0], data=urlencode(params)),
                               headers=search_header,
                               meta=meta_dat,
                               callback=self.get_paper_divs,
                               dont_filter=True
                               ))
        print('\n=>request search urls: ')
        print(reqs)
        if len(reqs) < 1:
            print('No search result!')
            exit(1)
        return reqs

    def get_paper_divs(self, response):
        reqs = list()
        paper_divs = response.css('#gs_res_ccl_mid > div')
        for paper_div in paper_divs:
            data_cid = paper_div.xpath('./@data-cid').extract_first()
            new_url = 'http://scholar.google.com/scholar?q=info:{data_cid}:scholar.google.com' \
                      '/&output=cite&scirp=1&hl=en'.format(
                data_cid=data_cid)
            reqs.append(scrapy.Request(new_url, meta={'SeqNum': response.meta['SeqNum']}, callback=self.get_bibtex_urls,
                                       dont_filter=True))
        print('\n=>request papers\' urls: ')
        print(reqs)
        if len(reqs) < 1:
            print('No papers!')
            exit(1)
        return reqs

    def get_bibtex_urls(self, response):
        reqs = list()
        cite_nodes = response.selector.css('.gs_citi')
        for node in cite_nodes:
            if 'BibTeX' == node.xpath('string(.)').extract_first():
                bibtex_url = node.xpath('./@href').extract_first()
                bibtex_url = bibtex_url.replace('https', 'http')
                reqs.append(scrapy.Request(bibtex_url, meta={'SeqNum': response.meta['SeqNum']},
                                           callback=self.get_bibtex_contents, dont_filter=True))
        print('\n=>request bibtex urls: ')
        print(reqs)
        if len(reqs) < 1:
            print('No bibtex!')
            exit(1)
        return reqs

    def get_bibtex_contents(self, response):
        bibtex_item = BibTeXScriptItem()
        bibtex_item['BibTeX'] = response.text
        # 希望根据titles来排序
        bibtex_item['SeqNum'] = response.meta['SeqNum']
        print('=> got BibTex: ')
        print(bibtex_item['BibTeX'])
        return [bibtex_item]
