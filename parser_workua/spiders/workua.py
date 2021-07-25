import scrapy


class WorkuaSpider(scrapy.Spider):
    name = 'workua'
    allowed_domains = ['work.ua']
    start_urls = ['https://www.work.ua/resumes-kharkiv/']
    pagination_page_count = 2

    def parse(self, response):

        for item in response.css('div#pjax-resume-list div.card.resume-link'):

            vacancy_uri = item.css('h2 a::attr(href)').get()

            workers = {
                'position': item.css('h2 a::text').get(),
                'name': item.css('div b::text').get(),
                'link': 'https://www.work.ua' + vacancy_uri,
            }

            salary = item.css('h2 span.normal-weight span::text').get()
            if salary:
                workers['salary'] = float(salary.replace(' грн', ''))

            yield response.follow(vacancy_uri, self.parse_vacncy, meta={
                'workers': workers
            })

        for page in response.css('ul.pagination li:last-child')[:self.pagination_page_count]:
            if page.css('a::text').get() == 'Наступна':
                yield response.follow(
                    page.css('a::attr(href)').get(),
                    self.parse
                )

    def parse_vacncy(self, response):

        header_text = response.css('div.card > h2:not(#contactInfo)::text').get()

        desc_text = ' '.join(response.css('div.card > p.text-muted:not(#contactMessageHint)::text').getall())
        desc_text = ' '.join(desc_text.split())

        worker_age = response.css('div.card div.row div dl.dl-horizontal dd::text').get()
        worker_age = ' '.join(worker_age.split())

        response.meta['workers']['age'] = worker_age
        response.meta['workers']['description'] = header_text + ": " + desc_text

        yield response.meta['workers']
