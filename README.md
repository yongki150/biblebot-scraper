<h2 align="center">Biblebot Scraper</h2>
<p align="center">
<a href="https://www.python.org/downloads/release/python-370/"><img alt="Python" src="https://img.shields.io/badge/python-3.7-blue?logo=python&logoColor=white"></a>
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
</p>

성서봇 스크래이퍼는 한국성서대학교와 연관된 정보를 수집할 수 있는 파이썬 패키지입니다.

이 패키지를 바탕으로, **성서봇** 모바일 애플리케이션(Android/IOS)이 한국성서대학교학생들에게 2018년부터 실서비스 되고 있습니다.  
  
이 패키지는 크게 세 가지 웹사이트에 대한 스크래이퍼를 제공합니다.
  
1. [한국성서대학교 인트라넷](https://kbuis.bible.ac.kr/) 스크래이퍼  
2. [한국성서대학교 홈페이지](https://www.bible.ac.kr/) 스크래이퍼  
3. [OKPOS 마일리지 시스템](https://asp.netusys.com/) 스크래이퍼  
  
  
## Installation
현재 테스트 배포 중입니다.

```
$ pip install -i https://test.pypi.org/simple/ 'biblebot[http]' --extra-index-url https://pypi.org/simple
```

## Dependencies
    - `beautifulsoup4`: html과 xml 에서 데이터를 추출하기 위해 사용합니다.
	- `aiohttp`: HTTP 요청을 위해 사용합니다. (OPTIONAL)


HTTP 요청을 위해 HTTP 요청 패키지가 필요합니다. `aiohttp` 또는 `requests` 패키지가 존재할 경우 자동으로 인식하여 사용합니다.

그 외의 HTTP 요청 패키지를 이용하고 싶다면 `BaseRequest` 추상클래스를 상속받아 구현한 뒤, `HTTPClient.set`을 이용하여 등록해 사용할 수 있습니다.

