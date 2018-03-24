# -*- coding: utf-8 -*-
import scrapy
from scrapy import Spider, Request
from datetime import datetime
import time
from MuseumNews.items import MuseumnewsItem

beginTime=input("请输入开始时间(格式为年-月-日):")
endTime=input("请输入结束时间(格式为年-月-日):")

#转换成时间戳
bt = int(time.mktime(time.strptime(beginTime, "%Y-%m-%d")))
et = int(time.mktime(time.strptime(endTime, "%Y-%m-%d")))

startPage=1

#设置URL的格式
URL="http://news.baidu.com/ns?word=%E5%8D%9A%E7%89%A9%E9%A6%86&pn={page}&cl=2&ct=0&tn=newsdy&rn=40&ie=utf-8&bt={bt}&et={et}"

class NewspiderSpider(Spider):
    name = 'Newspider'
    allowed_domains = ['news.baidu.com']
    page=startPage
    start_urls = [URL.format(page=(page-1)*40,bt=bt,et=et)]
    end=False
    flag=set()
    dt=datetime.strftime(datetime.now(),"%Y-%m-%d")
    def parse(self, response):
        # 先抓大后抓小
        res=response.xpath('//div[@class="result"]')
        if not res:
            self.end=True
            return

        for each in res:
            title=each.xpath('h3/a//text()').extract()
            title=''.join(title)
            if title in self.flag:
                self.end=True
                return
            self.flag.add(title)

            ans = each.xpath('div//p[@class="c-author"]/text()').extract_first().split()
            author = ans[0]
            ptime = ''.join(ans[1])
            if ptime.find('年') != -1:
                ptime = ptime.replace('年', '-').replace('月', '-').replace('日', '')
            else:
                ptime = self.dt

            #有图片的情况
            remark=each.xpath('div/div[@class="c-span18 c-span-last"]//text()').extract()[1:]
            remark=''.join(remark).replace('百度快照', '').replace('...', '').replace('查看更多相关新闻>>', '')

            #没有图片的情况
            if not remark.strip():
                remark=each.xpath('div//text()').extract()[1:]
                remark=''.join(remark).replace('百度快照', '').replace('...', '').replace('查看更多相关新闻>>', '')

            url=each.xpath('h3[@class="c-title"]/a/@href').extract()[0]

            item=MuseumnewsItem()
            item['title']=title
            item['author']=author
            item['ptime']=ptime
            item['remark']=remark
            item['url']=url
            yield item

        if not self.end:
            self.page=self.page+1
            yield Request(URL.format(page=(self.page-1)*40,bt=bt,et=et),self.parse)


