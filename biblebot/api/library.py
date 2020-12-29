from typing import Dict, Optional, List
from base64 import b64encode
import re

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
    "CheckoutList",
    "BookPhoto",
)

DOMAIN_NAME: str = "https://lib.bible.ac.kr"

_ParserPrecondition = ParserPrecondition(IParserPrecondition)


class _SessionExpiredChecker(IParserPrecondition):
    @staticmethod
    def is_blocking(response: Response) -> Optional[ErrorData]:
        if response.status == 302:
            return ErrorData(
                error={"title": "세션이 만료되어 로그인페이지로 리다이렉트 되었습니다."}, link=response.url
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
            "http://lib.bible.ac.kr",
            cookies=cookies,
            headers=headers,
            timeout=timeout,
            **kwargs,
        )

    @classmethod
    def parse(cls, response: Response, cookies: Dict[str, str]) -> APIResponseType:
        soup = response.soup
        ul = soup.select_one("#sponge-header .infoBox")
        li = ul.select("li")[1].text
        iat = httpdate_to_unixtime(response.headers["date"])

        if li == "HOME":
            return ErrorData(
                error={"title": "로그인에 실패하였습니다. 정확한 정보를 입력하세요."},
                link=response.url,
            )

        return ResourceData(
            data={
                "cookies": cookies,
                "validate-content": li,
                "iat": iat,
            },
            link=response.url,
        )


class CheckoutList(IParser):
    URL: str = DOMAIN_NAME + "/MyLibrary"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            cls.URL, cookies=cookies, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    async def fetch_detail(
        cls,
        detail_url,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            detail_url, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse_detail(cls, response: Response) -> List[str]:
        soup = response.soup

        isbn = soup.select("#detailtoprightnew .sponge-book-list-data")[1].text.strip()
        img_url = soup.select_one(".page-detail-title-image a img")["src"]

        if not re.match(r"https?://", img_url):
            img_url = None

        return [isbn, img_url]

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

        # head 는 ['ISBN', '서지정보', '대출일자', '반납예정일', '대출상태', '연기신청', '도서이미지']로 구성되어있습니다.
        head: List[str] = [th.text.strip() for th in thead.select("th")]
        del head[4]
        head[0] = "ISBN"
        head[-1] = "도서이미지"

        return head

    @classmethod
    def parse_main_table(cls, response: Response) -> List[List]:
        soup = response.soup

        tbody = soup.select(".sponge-guide-Box-table tbody tr")
        body = []

        if not tbody:
            raise ParsingError("테이블 바디가 존재하지 않습니다.", response)

        for tr in tbody:
            info = [td.text.strip() for td in tr.select("td")]
            info[1] = tr.select_one("td a strong").text.strip()
            info[-1] = tr.select(".left a")[0]["href"]
            del info[4]

            body.append(info)
        return body


class BookPhoto:
    @classmethod
    async def fetch(
        cls,
        photo_url,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            photo_url, headers=headers, timeout=timeout, **kwargs
        )
