from typing import Dict, Union
from base64 import b64encode
from io import BytesIO
from pprint import pprint

from aiounittest import AsyncTestCase
from PIL import Image

from biblebot.api import LibraryAPI
import biblebot


def get_image_info(raw_img: bytes) -> Dict[str, Union[int, str]]:
    img = Image.open(BytesIO(raw_img))
    width, height = img.size
    fmt = img.format
    return {
        "width": width,
        "height": height,
        "format": fmt,
        "img": b64encode(raw_img).decode(),
    }


def _filter_usable_book_path(path: str):
    import re
    find = re.compile(r"^\/Search\/Detail\/(\d*)$")

    return re.match(find, path)


class Test(AsyncTestCase):
    # Enter your info
    USERNAME: str = ""
    PASSWORD: str = ""

    # Assign later
    SESSION_COOKIES: str = ""

    def setUp(self) -> None:
        print("\n")

    def tearDown(self) -> None:
        print()

    @classmethod
    async def test_login_scraper(cls):
        response = await LibraryAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
        result = LibraryAPI.Login.parse(response)
        cls.SESSION_COOKIES = result.data["cookies"]

        print("로그인")
        pprint(result.data)

    @classmethod
    async def test_checkout_list_scraper(cls):
        if not cls.SESSION_COOKIES:
            response = await LibraryAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
            result = LibraryAPI.Login.parse(response)
            cls.SESSION_COOKIES = result.data["cookies"]

        response = await LibraryAPI.CheckoutList.fetch(cls.SESSION_COOKIES)
        result = LibraryAPI.CheckoutList.parse(response)

        print("대출 목록")
        pprint(result.data)

    @classmethod
    async def test_book_detail_scraper(cls):
        if not cls.SESSION_COOKIES:
            response = await LibraryAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
            result = LibraryAPI.Login.parse(response)
            cls.SESSION_COOKIES = result.data["cookies"]

        response = await LibraryAPI.CheckoutList.fetch(cls.SESSION_COOKIES)
        result = LibraryAPI.CheckoutList.parse(response)

        result.data["head"][0] = "ISBN"
        result.data["head"][-1] = "도서 이미지 URL"

        for book in result.data["body"]:
            path = book[-1]
            if not _filter_usable_book_path(path):
                continue

            response = await LibraryAPI.BookDetail.fetch(path)
            isbn, image_url = LibraryAPI.BookDetail.parse(response)
            book[0] = isbn
            book[-1] = image_url

        print("대출 목록 + 상세 정보")
        pprint(result.data)

    @classmethod
    async def test_book_detail_scraper_at_non_checkout(cls):
        path_list = [
            "/Search/Detail/161595",                        # valid path
            "/Search/Detail/%EA%B9%80%EA%B8%B0%EC%A0%95"    # not valid path
        ]

        print("대출 목록 없을시 + 상세 정보")

        for path in path_list:
            if not _filter_usable_book_path(path):
                continue

            response = await LibraryAPI.BookDetail.fetch(path)
            isbn, image_url = LibraryAPI.BookDetail.parse(response)

            print("ISBN: ", isbn)
            print("IMAGE URL: ", image_url)

    @classmethod
    async def test_book_photo_scraper(cls):
        if not cls.SESSION_COOKIES:
            response = await LibraryAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
            result = LibraryAPI.Login.parse(response)
            cls.SESSION_COOKIES = result.data["cookies"]

        response = await LibraryAPI.CheckoutList.fetch(cls.SESSION_COOKIES)
        result = LibraryAPI.CheckoutList.parse(response)

        result.data["head"][0] = "ISBN"
        result.data["head"][-1] = "도서 이미지"

        for book in result.data["body"]:
            path = book[-1]
            if not _filter_usable_book_path(path):
                continue

            response = await LibraryAPI.BookDetail.fetch(path)
            isbn, photo_url = LibraryAPI.BookDetail.parse(response)
            book[0] = isbn
            book[-1] = photo_url

            if photo_url:
                response = await LibraryAPI.BookPhoto.fetch(photo_url)
                photo_result = LibraryAPI.BookPhoto.parse(response)

                book[-1] = (
                    get_image_info(photo_result.data["raw_image"])
                    if isinstance(photo_result, biblebot.ResourceData)
                    else None
                )
            else:
                book[-1] = {
                    "width": 0,
                    "height": 0,
                    "format": None,
                    "img": None,
                }

        print("대출 목록 API 최종")
        pprint(result.data)
