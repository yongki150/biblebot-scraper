"""
##### 대출목록 기능 #####
CheckoutList → BookDetail → BookPhoto를 거쳐야만 데이터가 취합되는 구조이다.
CheckoutList를 통해
['No', '서지정보', '대출일자', '반납예정일', '대출상태', '연기신청', '상세페이지 URL']의 데이터가

BookDetail과 BookPhoto를 통해
['ISBN', '서지정보', '대출일자', '반납예정일', '대출상태', '연기신청', '도서이미지']의 데이터가 완성된다.
"""
from typing import Dict, Optional, List, Tuple
from base64 import b64encode
import unicodedata
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
from ..api.intranet import IParserPrecondition
from .common import httpdate_to_unixtime, parse_table

__all__ = (
    "Login",
    "CheckoutList",
    "BookDetail",
    "BookPhoto",
    "NewBookPath",
    "BookIntro",
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
    def parse(cls, response: Response) -> APIResponseType:
        soup = response.soup
        # 로그인 실패: 잘못된 입력값
        if "location" not in response.headers:
            alert = soup.select_one(".alert-warning").text.strip()
            return ErrorData(error={"title": alert}, link=response.url)
        # 로그인 실패: 인코딩, 경로이탈
        m = re.search(r"ErrorCode=(\d+)", response.headers["location"])
        if m:
            error_code = m.group(1)
            return ErrorData(
                error={"title": "잘못된 경로입니다.", "code": error_code}, link=response.url
            )
        # 로그인 성공
        else:
            iat = httpdate_to_unixtime(response.headers["date"])
            return ResourceData(
                data={"cookies": response.cookies, "iat": iat}, link=response.url
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
    def _parse_main_table(cls, response: Response) -> Tuple[List, List]:
        soup = response.soup
        thead = soup.select_one(".sponge-table-default thead")
        tbody = soup.select_one(".sponge-table-default tbody")
        head, body = parse_table(response, thead, tbody)

        del head[4]
        head[-1] = "상세페이지 URL"

        for tr, each in zip(tbody.select("tr"), body):
            del each[4]
            each[1] = tr.select_one("td a strong").text.strip()
            each[-1] = tr.select_one(".left a")["href"]
        return head, body

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        head, body = cls._parse_main_table(response)
        if not body:
            return ErrorData(error={"title": "대출한 내역이 없습니다."}, link=response.url)

        return ResourceData(data={"head": head, "body": body}, link=response.url)


class BookDetail:
    @classmethod
    async def fetch(
        cls,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            DOMAIN_NAME + path, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> List[str]:
        soup = response.soup
        isbn = soup.select("#detailtoprightnew .sponge-book-list-data")[1].text.strip()
        title = soup.select_one(".sponge-book-title").text.strip()
        img_url = soup.select_one(".page-detail-title-image a img")["src"]

        find = re.compile(r"^([^\s]*)")
        isbn = re.search(find, isbn).group()

        if not re.match(r"https?://", img_url):
            img_url = None

        return [isbn, title, img_url]


class BookPhoto:
    @classmethod
    async def fetch(
        cls,
        photo_url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            photo_url, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> APIResponseType:
        if response.headers["content-type"][:5] == "image":
            return ResourceData(data={"raw_image": response.raw}, link=response.url)


class NewBookPath:
    URL: str = DOMAIN_NAME + "/Search/New"

    @classmethod
    async def fetch(
        cls,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            cls.URL, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> List[str]:
        soup = response.soup
        new_book_path_list = soup.select(".sponge-newbook-list > li")
        new_book_path_list = [book.select_one("a")["href"] for book in new_book_path_list]

        return new_book_path_list


class BookIntro:
    URL: str = DOMAIN_NAME + "/Naver/NaverDetail?isbn="

    @classmethod
    async def fetch(
        cls,
        isbn: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await HTTPClient.connector.get(
            cls.URL + isbn, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> Optional[str]:
        soup = response.soup
        div = soup.find(class_="sponge-page-guide")
        try:
            introduction = div.find("div", attrs={"id": "bookIntroContent"}).get_text()
            introduction = unicodedata.normalize("NFKD", introduction)

            find = re.compile(r"^(([^.]*).){2}")
            introduction = re.search(find, introduction).group()
        except AttributeError:
            introduction = None

        return introduction
