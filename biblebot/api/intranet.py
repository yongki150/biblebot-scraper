from abc import ABCMeta, abstractmethod
from typing import Optional, Dict, List, Tuple
import re

from .base import (
    HTTPClient,
    IParser,
    APIResponseType,
    ILoginFetcher,
    ISemesterFetcher,
    ResourceData,
    ErrorData,
    ParserPrecondition,
    SemesterData,
)
from ..reqeust import Response
from ..exceptions import ParsingError
from .common import (
    httpdate_to_unixtime,
    extract_alerts,
    extract_hidden_tags,
    urlencode,
    parse_table,
)

__all__ = (
    "IParserPrecondition",
    "Login",
    "StudentPhoto",
    "Chapel",
    "Timetable",
    "Course",
)

DOMAIN_NAME: str = "https://kbuis.bible.ac.kr"  # with protocol
_SEMESTER_KEY: str = "ctl00$ContentPlaceHolder1$cbo_YearHg"


class IParserPrecondition(metaclass=ABCMeta):
    @staticmethod
    @abstractmethod
    def is_blocking(response: Response) -> Optional[ErrorData]:
        """ 진행할 수 없는 사전조건인 경우 ErrorData, 그렇지 않은 경우 None """
        pass


_ParserPrecondition = ParserPrecondition(IParserPrecondition)


class _SessionExpiredChecker(IParserPrecondition):
    @staticmethod
    def is_blocking(response: Response) -> Optional[ErrorData]:
        alerts = extract_alerts(response.soup)
        for alert in alerts:
            if "세션" in alert or "수업평가" in alert:
                return ErrorData(
                    error={"title": alert, "alert_messages": alerts}, link=response.url
                )
        return None


def _extract_semester(response: Response) -> SemesterData:
    select_tag = response.soup.find("select", attrs={"name": _SEMESTER_KEY})
    if not select_tag:
        raise ParsingError("학기 셀렉트 태그를 찾을 수 없습니다.", response)
    options = select_tag.find_all("option", selected=True)
    if not options:
        raise ParsingError("학기 옵션 태그를 찾을 수 없습니다.", response)

    try:
        selectables: List[str] = [
            opt.attrs["value"] for opt in select_tag.find_all("option")
        ]
        selected: str = select_tag.find("option", selected=True).attrs["value"]
    except (KeyError, AttributeError):
        raise ParsingError("학기 옵션 태그를 정상적으로 선택할 수 없습니다.", response)
    return SemesterData(selected=selected, selectable=selectables)


async def _post_with_semester(
    url,
    cookies: Dict[str, str],
    semester: Optional[str] = None,
    *,
    headers: Optional[Dict[str, str]] = None,
    timeout: Optional[float] = None,
    **kwargs,
) -> Response:
    """ 인트라넷에서 특정 학기의 정보 조회를 위한 메서드

    특정 학기 조회를 위해서는 POST 메서드로 정보를 전송해야하는데, 그 전에 hidden 태그를 함께 보내야함.
    1. GET 요청, 해당 페이지를 불러와서 form hidden-tag 의 (name,key) 쌍을 얻는다.
        - 여기서 얻는 정보는 학교에서 미리 지정해놓은터 학기, 일반적으로 최신 학기
    2. POST 요청, hidden-tag와 학기를 body에 담아 전송한다.
    """
    response = await HTTPClient.connector.get(
        url, cookies=cookies, headers=headers, timeout=timeout, **kwargs
    )
    if _SessionExpiredChecker.is_blocking(response):
        return response

    semester_info: SemesterData = _extract_semester(response)
    if (
        semester
        and semester != semester_info.selected
        and semester in semester_info.selectable
    ):
        body = extract_hidden_tags(response.soup)
        body[_SEMESTER_KEY] = semester
        body["ctl00$ContentPlaceHolder1$hidActionMode"] = "S"
        response = await HTTPClient.connector.post(
            url, body=body, cookies=cookies, headers=headers, timeout=timeout, **kwargs
        )
        semester_info: SemesterData = _extract_semester(response)
    response.etc["semester"] = semester_info
    return response


class Login(ILoginFetcher, IParser):
    # TODO: URL 변경 유의
    URL: str = DOMAIN_NAME + "/ble_login2.aspx"

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
        form = {"Txt_1": user_id, "Txt_2": user_pw, "use_type": "2"}
        return await HTTPClient.connector.post(
            cls.URL, headers=headers, body=form, timeout=timeout, **kwargs
        )

    @classmethod
    def parse(cls, response: Response) -> APIResponseType:
        """
        로그인 성공: status 302, location header 포함, 리다이렉트 메시지를 body에 포함
        로그인 실패: status 200, location header 미포함, alert 메시지룰 body에 포함
        """
        # Login 성공
        if response.status == 302:
            iat = httpdate_to_unixtime(response.headers["date"])
            return ResourceData(
                data={"cookies": response.cookies, "iat": iat}, link=response.url
            )
        # TODO: 현 인트라넷 서버 과부하 상황이 없애지면 더 자세한 조건 추가할 예정
        # Login 실패: 인트라넷 서버 과부하
        elif response.status == 503:
            return ErrorData(
                error={
                    "title": response.soup.find("h2").get_text(),
                    "error_message": response.soup.find("p").get_text()
                },
                link=response.url
            )
        # Login 실패: Common 한 오류
        else:
            alerts: List[str] = extract_alerts(response.soup)
            alert = alerts[0] if alerts else ""
            return ErrorData(
                error={"title": alert, "alert_messages": alerts}, link=response.url
            )


class StudentPhoto(IParser):
    URL: str = DOMAIN_NAME + "/SchoolRegMng/SR015.aspx"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        sid: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        query: Dict[str, str] = {"schNo": sid}
        query_string = urlencode(query)
        url = f"{cls.URL}?{query_string}"
        return await HTTPClient.connector.get(
            url, cookies=cookies, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        """
        사진을 불러온 경우:
            headers= {'transfer-encoding': 'chunked', 'content-type': 'image/jpeg', 'content-disposition': 'attachment;filename=image.jpeg'}
        사진을 불러오지 못한 경우:
            headers= {'transfer-encoding': 없음, 'content-type': 'text/html; charset=ks_c_5601-1987', 'content-disposition': 없음}
        """
        if response.headers["content-type"][:5] == "image":
            return ResourceData(data={"raw_image": response.raw}, link=response.url)
        else:
            return ErrorData(error={"title": "이미지를 불러올 수 없습니다."}, link=response.url)


class Chapel(ISemesterFetcher, IParser):
    URL: str = DOMAIN_NAME + "/StudentMng/SM050.aspx"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        semester: Optional[str] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await _post_with_semester(
            cls.URL, cookies, semester, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def _parse_summary(cls, response: Response) -> Dict[str, str]:
        soup = response.soup
        tbody = soup.find("tbody", attrs={"class": "mbody"})
        if not tbody:
            raise ParsingError("채플 요약 테이블을 찾을 수 없습니다.", response)

        summary: Dict[str, str] = {}
        th_list = tbody.find_all("th")[1:]
        td_list = tbody.find_all("td")[:-1]
        for th, td in zip(th_list, td_list):
            key = th.get_text(strip=True)
            value = td.get_text(strip=True)

            day_count = re.search(r"\d+", value)
            summary[key] = str(day_count.group()) if day_count else ""

        summary["지각"] = summary.pop("지각일수")
        summary["출석"] = summary.pop("출석일수")
        summary["확정"] = summary.pop("확정일수")

        tbody = soup.find("tbody", attrs={"class": "viewbody"})
        th = tbody.find("th").get_text(strip=True)
        td = tbody.find("td").get_text(strip=True)
        summary[th] = str(re.search(r"\d+", td).group())
        return summary

    @classmethod
    def _parse_main_table(cls, response: Response) -> Tuple[List, List]:
        soup = response.soup
        thead = soup.find("thead", attrs={"class": "mhead"})
        tbody = soup.find_all("tbody", attrs={"class": "mbody"})[1]
        head, body = parse_table(response, thead, tbody)
        del head[5]
        for each in body:
            del each[5]
        return head, body

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        summary = cls._parse_summary(response)
        head, body = cls._parse_main_table(response)

        return ResourceData(
            data={"summary": summary, "head": head, "body": body,},
            link=response.url,
            meta={
                "selected": response.etc["semester"].selected,
                "selectable": response.etc["semester"].selectable,
            },
        )


class Timetable(ISemesterFetcher, IParser):
    URL: str = DOMAIN_NAME + "/GradeMng/GD160.aspx"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        semester: Optional[str] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await _post_with_semester(
            cls.URL, cookies, semester, headers=headers, timeout=timeout, **kwargs
        )

    @staticmethod
    def _parse_contents(td: str, response: Response) -> Tuple:
        matching = re.match(
            r"(.+)?\(([^(]*)?\)(\d{2}:\d{2})\s*~\s*([0-9:]{,5})", td
        ) or re.match(r"(.+)?()(\d{2}:\d{2})\s*~\s*([0-9:]{,5})", td)
        if not matching:
            ParsingError("시간표 상세정보를 해석할 수 없습니다.", response)
        return matching.groups()

    @classmethod
    def _parse_main_table(cls, response: Response) -> Tuple[List, List]:
        soup = response.soup
        thead = soup.find("thead", attrs={"class": "mhead"})
        tbody = soup.find("tbody", attrs={"class": "mbody"})
        result = [[], [], [], [], []]
        head, body = parse_table(response, thead, tbody)

        for row in body:
            for i, each in enumerate(row):
                if each:
                    result[i].append(cls._parse_contents(each, response))

        return head, result

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        head, body = cls._parse_main_table(response)
        return ResourceData(
            data={"head": head, "body": body},
            link=response.url,
            meta={
                "selected": response.etc["semester"].selected,
                "selectable": response.etc["semester"].selectable,
            },
        )


class Course(ISemesterFetcher, IParser):
    URL: str = DOMAIN_NAME + "/GradeMng/GD095.aspx"

    @classmethod
    async def fetch(
        cls,
        cookies: Dict[str, str],
        semester: Optional[str] = None,
        *,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Response:
        return await _post_with_semester(
            cls.URL, cookies, semester, headers=headers, timeout=timeout, **kwargs
        )

    @classmethod
    def _parse_main_table(cls, response: Response) -> Tuple[List, List]:
        soup = response.soup
        thead = soup.find("thead", attrs={"class": "mhead"})
        tbody = soup.find("tbody", attrs={"class": "mbody"})

        return parse_table(response, thead, tbody)

    @classmethod
    @_ParserPrecondition
    def parse(cls, response: Response) -> APIResponseType:
        head, body = cls._parse_main_table(response)
        return ResourceData(
            data={"head": head, "body": body},
            link=response.url,
            meta={
                "selected": response.etc["semester"].selected,
                "selectable": response.etc["semester"].selectable,
            },
        )
