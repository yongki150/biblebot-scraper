<h1 align="center">Biblebot Scraper</h1>
<p align="center">
<a href="https://www.python.org/downloads/release/python-370/"><img alt="Python" src="https://img.shields.io/badge/python-3.7-blue?logo=python&logoColor=white"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

성서봇 스크래이퍼는 한국성서대학교와 연관된 정보를 수집할 수 있는 파이썬 패키지입니다.

이 패키지를 바탕으로, **성서봇** 모바일 애플리케이션([Android](https://play.google.com/store/apps/details?id=com.blogspot.ramming125.kbubot&hl=ko) / [IOS](https://apps.apple.com/kr/app/성서봇/id1441276020))이 한국성서대학교학생들에게 2018년부터 실서비스 되고 있습니다.  

이 패키지는 네 가지 웹사이트에 대한 스크래이퍼를 제공합니다.

1. [한국성서대학교 인트라넷](https://kbuis.bible.ac.kr/) 스크래이퍼  
2. [한국성서대학교 LMS](https://lms.bible.ac.kr/) 스크래이퍼
3. [한국성서대학교 홈페이지](https://www.bible.ac.kr/) 스크래이퍼  
4. [OKPOS 마일리지 시스템](https://asp.netusys.com/) 스크래이퍼  




## Installation
```
$ pip install 'biblebot[http]'
```



## Dependencies

    - `beautifulsoup4`: html과 xml 에서 데이터를 추출하기 위해 사용합니다.
    - `aiohttp`: HTTP 요청을 위해 사용합니다. (OPTIONAL)


HTTP 요청을 위해 HTTP 요청 패키지가 필요합니다. `aiohttp` 또는 `requests` 패키지가 존재할 경우 자동으로 인식하여 사용합니다.

그 외의 HTTP 요청 패키지를 이용하고 싶다면 `BaseRequest` 추상클래스를 상속받아 구현한 뒤, `HTTPClient.set`을 이용하여 등록해 사용할 수 있습니다.



## Documentation

[APIs document](docs/APIs.md)



## Get started

### 공지사항 가져오기

````python
import asyncio
from pprint import pprint

from biblebot import KbuAPI


async def main():
    resp = await KbuAPI.MainNotice.fetch(page=2)  # 공지사항 2페이지
    result = KbuAPI.MainNotice.parse(resp)
    pprint(result.data)

asyncio.run(main())
````

**Output:**

```json
{
    "notice": [
        {
            "seq": "3742",
            "title": "[대학원 입시] 2020학년도 후기 한국성서대학교 대학원 신입생 모집",
            "author": "장성희",
            "date": "2020-07-31",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46649?p=2"
        },
        {
            "seq": "3741",
            "title": "[기초교육원] 2020-2학기 수강신청 기초교육원, 영어교육센터 공지사항 안내",
            "author": "김다윗",
            "date": "2020-07-30",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46645?p=2"
        },
        {
            "seq": "3740",
            "title": "[학적] 2020-2학기 적용 융합모듈 교육과정 승인자 발표",
            "author": "김희",
            "date": "2020-07-30",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46644?p=2"
        },
        {
            "seq": "3739",
            "title": "[학적] 2020-2학기 적용 부전공 승인자 발표",
            "author": "김희",
            "date": "2020-07-30",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46643?p=2"
        },
        {
            "seq": "3738",
            "title": "[학적] 2020-2학기 적용 복수전공 승인자 발표",
            "author": "김희",
            "date": "2020-07-30",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46641?p=2"
        },
        {
            "seq": "3737",
            "title": "[학적] 2020-2학기 적용 전과 승인자 발표",
            "author": "김희",
            "date": "2020-07-30",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46640?p=2"
        },
        {
            "seq": "3736",
            "title": "[수업] 2020-2학기 개설강좌 및 시간표 발표 안내",
            "author": "유다운",
            "date": "2020-07-28",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46633?p=2"
        },
        {
            "seq": "3735",
            "title": "[생활관] 2020-2학기 생활관 입주 신청 공고",
            "author": "조철남",
            "date": "2020-07-28",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46631?p=2"
        },
        {
            "seq": "3734",
            "title": "[학적] 2019학년도 후기 학위수여자 발표",
            "author": "김희",
            "date": "2020-07-24",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46617?p=2"
        },
        {
            "seq": "3733",
            "title": "[학점교류] 2020-2학기 서울여자대학교 학점교류 신청 안내",
            "author": "유다운",
            "date": "2020-07-24",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46616?p=2"
        },
        {
            "seq": "3732",
            "title": "[규정] 20-7월 규정 개정 공고",
            "author": "윤경민",
            "date": "2020-07-23",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46615?p=2"
        },
        {
            "seq": "3731",
            "title": "[수업] 2020-하계계절학기 성적 확인 및 이의신청 안내",
            "author": "유다운",
            "date": "2020-07-23",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46614?p=2"
        },
        {
            "seq": "3730",
            "title": "[대학인사] 2020년 장애대학생 교육복지지원 실태평가 위원회 및 보직변경에 따른 위원회 임명",
            "author": "김현동",
            "date": "2020-07-23",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46612?p=2"
        },
        {
            "seq": "3729",
            "title": "[수업] 2020-2학기 수강신청 안내 (수정 7/24)",
            "author": "유다운",
            "date": "2020-07-17",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46603?p=2"
        },
        {
            "seq": "3728",
            "title": "[채용] 컴퓨터소프트웨어학과 실습조교 채용 재공고(~7/24까지)",
            "author": "김병수",
            "date": "2020-07-17",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46601?p=2"
        },
        {
            "seq": "3727",
            "title": "[산학협력단] 2020년도 학술지지원사업(인문사회분야) 신규과제 공모",
            "author": "윤경민",
            "date": "2020-07-16",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46599?p=2"
        },
        {
            "seq": "3726",
            "title": "(코로나) 대학생 대면모임 및 활동 등 자제 협조 요청(교육부 공문)",
            "author": "김병수",
            "date": "2020-07-14",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46598?p=2"
        },
        {
            "seq": "3725",
            "title": "일립관 승강기(7층) 운행 중지 안내",
            "author": "이은광",
            "date": "2020-07-14",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46597?p=2"
        },
        {
            "seq": "3724",
            "title": "[채용] 컴퓨터소프트웨어학과 실습조교 채용 공고(~7/16까지)",
            "author": "김병수",
            "date": "2020-07-09",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46593?p=2"
        },
        {
            "seq": "3723",
            "title": "[수업] 2020-1학기 성적 이의신청 안내",
            "author": "유다운",
            "date": "2020-07-09",
            "url": "https://www.bible.ac.kr/ko/life/notice/view/46591?p=2"
        }
    ]
}
```



### 수강하는 강의 정보 가져오기

```python
import asyncio
from pprint import pprint

from biblebot import IntranetAPI


async def main():
    account = ("본인 아이디", "본인 패스워드")

    # Login
    resp = await IntranetAPI.Login.fetch(*account)
    result = IntranetAPI.Login.parse(resp)
    cookie = result.data["cookies"]

		# Get course information
    resp = await IntranetAPI.Course.fetch(cookies=cookie, semester="20201")
    result = IntranetAPI.Course.parse(resp)
    pprint(result.data)
    
asyncio.run(main())
```

**Output:**

```json
{
    "head": [
        "강좌코드",
        "강좌명",
        "이수구분",
        "학점",
        "교수명",
        "강의시간",
        "선택",
        "비고"
    ],
    "body": [
        [
            "GE264-A",
            "경건훈련",
            "기초공통필수",
            "0",
            "유정선",
            "(수)12:00~12:30",
            "",
            "NO"
        ],
        [
            "GE495-N",
            "전도훈련Ⅶ",
            "기초공통필수",
            "0",
            "최영태",
            "(수)13:30~15:20",
            "",
            "NO"
        ],
        [
            "GE748-A",
            "엑셀스프레드시트",
            "교양선택",
            "1",
            "한진호",
            "(월)14:55~16:10",
            "",
            "NO"
        ],
        [
            "IC122-A",
            "고급소프트웨어프로젝트",
            "전공선택",
            "3",
            "정해덕",
            "(화)14:55~16:10(목)14:55~16:10",
            "",
            "NO"
        ],
        [
            "IC134-D",
            "미래설계상담Ⅶ",
            "전공필수",
            "0",
            "정해덕",
            "(수)15:30~16:20",
            "",
            "NO"
        ],
        [
            "IC140-A",
            "빅데이터기술",
            "전공선택",
            "3",
            "양혜경",
            "(월)13:30~14:45(목)13:30~14:45",
            "",
            "NO"
        ],
        [
            "IC143-A",
            "종합설계I",
            "전공필수",
            "3",
            "정해덕",
            "(화)16:20~17:35(목)16:20~17:35",
            "",
            "NO"
        ],
        [
            "IC161-A",
            "창의적통합설계",
            "전공선택",
            "3",
            "현우석",
            "(월)16:20~17:35(화)13:30~14:45",
            "",
            "NO"
        ]
    ]
}
```



더 많은 기능은 [여기](docs/APIs.md)서 확인하세요.