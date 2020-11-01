from typing import Dict, Optional, List
from base64 import b64encode

from .base import (
    ILoginFetcher,
    IParser,
    HTTPClient,
    APIResponseType,
    ResourceData,
    ErrorData,
    ParserPrecondition,
)
from ..reqeust.base import Response
from ..exceptions import ParsingError
from ..api.intranet import IParserPrecondition
from .common import httpdate_to_unixtime

__all__ = (
    "Login",
    "Library",
)

DOMAIN_NAME: str = "https://lib.bible.ac.kr"

_ParserPrecondition = ParserPrecondition(IParserPrecondition)

class _SessionExpiredChecker(IParserPrecondition):
    @staticmethod
    def is_blocking(response: Response) -> Optional[ErrorData]:
        if response.status == 302:
            return ErrorData(
                error={"title": "세션이 만료되어 로그인페이지로 리다이렉트 되었습니다."},
                link=response.url
            )
        return None

class Login(ILoginFetcher, IParser):
    URL: str = DOMAIN_NAME + "/Account/LogOn"

    @classmethod
    async def fetch(
            cls,
            user_id: str,
            user_pw: str,
            *,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            **kwargs,
    ) -> Response:
        form = {
            "l_id": b64encode(user_id.encode()).decode(),
            "l_pass": b64encode(user_pw.encode()).decode(),
        }
        return await HTTPClient.connector.post(
            cls.URL, headers=headers, body=form, timeout=timeout, **kwargs
        )

    @classmethod
    async def fetch_main_page(
            cls,
            cookies: Dict[str, str],
            *,
            headers: Optional[Dict[str, str]] = None,
            timeout: Optional[float] = None,
            **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            # https로 접속시 메인페이지로 접근이 불가능하는 이슈가 있습니다.
            "http://lib.bible.ac.kr", cookies=cookies, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response, cookies: Dict[str, str]) -> APIResponseType:
        soup = response.soup
        ul = soup.select_one('#sponge-header .infoBox')
        li = ul.select('li')[1].text

        iat = httpdate_to_unixtime(response.headers["date"])
        return ResourceData(
            data={
                "cookies": cookies,
                "validate-content": li,
                "iat": iat,
            },
            link=response.url
        )

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
    @_ParserPrecondition
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
        thead = soup.select_one(".sponge-guide-Box-table thead tr")

        if not thead:
            raise ParsingError("테이블 헤드가 존재하지 않습니다.", response)

        head: List[str] = [th.text.strip() for th in thead.select("th")]
        del head[4]

        return head

    @classmethod
    def parse_main_table(cls, response: Response) -> List[List]:
        soup = response.soup

        tbody = soup.select(".sponge-guide-Box-table tbody tr")
        body = []

        if not tbody:
            raise ParsingError("테이블 바디가 존재하지 않습니다.", response)

        for tr in tbody:
            num = tr.select_one(".right5").text
            num = num.replace("\n", "")

            title = tr.select_one("td a strong").text
            loan_date = tr.select(".left ul li strong")[0].text
            return_date = tr.select(".left ul li strong")[1].text
            state = tr.select_one("td .textcolorgreen").text

            term = tr.select("td")[6].text
            term = term.replace("\n", "")

            term_cnt = tr.select("td")[7].text
            term_cnt = term_cnt.replace("\n", "")

            info = [num, title, loan_date, return_date, state, term, term_cnt]

            body.append(info)

        return body
