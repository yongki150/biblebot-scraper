from typing import Dict, Optional, List

from biblebot.api.base import IParser, HTTPClient, APIResponseType, ResourceData
from biblebot.reqeust.base import Response
from biblebot.exceptions import ParsingError

__all__ = ('Library',)

DOMAIN_NAME: str = "https://lib.bible.ac.kr"


class Library(IParser):
    URL: str = DOMAIN_NAME + "/MyLibrary"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs
    ) -> Response:
        return await HTTPClient.connector.get(
            cls.URL, cookies=cookies, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> APIResponseType:
        head = cls.parse_subject(response)
        body = cls.parse_main_table(response)

        return ResourceData(
            data={"head": head, "body": body},
            link=response.url,
        )

    @classmethod
    def parse_subject(cls, response: Response) -> List[str]:
        soup = response.soup
        thead = soup.select_one('.sponge-guide-Box-table thead tr')

        if not thead:
            raise ParsingError("테이블 헤드가 존재하지 않습니다.", response)

        head: List[str] = [th.text.strip() for th in thead.select('th')]
        del head[4]

        return head

    @classmethod
    def parse_main_table(cls, response: Response) -> List[List]:
        soup = response.soup

        tr_s = soup.select('.sponge-guide-Box-table tbody tr')
        body = []

        if not tr_s:
            raise ParsingError("테이블 바디가 존재하지 않습니다.", response)

        for tr in tr_s:
            num = tr.select_one('.right5').text
            num = num.replace('\n', '')

            title = tr.select_one('td a strong').text
            loan_date = tr.select('.left ul li strong')[0].text
            return_date = tr.select('.left ul li strong')[1].text
            state = tr.select_one('td .textcolorgreen').text

            term = tr.select('td')[6].text
            term = term.replace('\n', '')

            term_cnt = tr.select('td')[7].text
            term_cnt = term_cnt.replace('\n', '')

            info = [num, title, loan_date, return_date, state, term, term_cnt]

            body.append(info)

        return body


