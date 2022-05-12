from typing import Dict, Optional

from aiounittest import AsyncTestCase

from biblebot.api import LmsAPI


class Test(AsyncTestCase):
    # Enter your info
    USERNAME: str = ""
    PASSWORD: str = ""
    SEMESTER: str = "20221"     # cf. year(2022) + semester(1)
    SESSION: Optional[Dict] = None

    def setUp(self) -> None:
        print("\n")

    def tearDown(self) -> None:
        print()

    @classmethod
    async def test_login_scraper(cls):
        response = await LmsAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
        result = LmsAPI.Login.parse(response)
        cls.SESSION = result.data["cookies"]

        print(result)

    @classmethod
    async def test_profile_scraper(cls):
        if cls.SESSION is None:
            response = await LmsAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
            result = LmsAPI.Login.parse(response)
            cls.SESSION = result.data["cookies"]

        response = await LmsAPI.Profile.fetch(cls.SESSION)
        result = LmsAPI.Profile.parse(response)

        print(result)

    @classmethod
    async def test_course_list_scraper(cls):
        if cls.SESSION is None:
            response = await LmsAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
            result = LmsAPI.Login.parse(response)
            cls.SESSION = result.data["cookies"]

        response = await LmsAPI.CourseList.fetch(
            cookies=cls.SESSION,
            semester=cls.SEMESTER
        )
        result = LmsAPI.CourseList.parse(response)

        print(result)

    @classmethod
    async def test_attendance_scraper(cls):
        if cls.SESSION is None:
            response = await LmsAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
            result = LmsAPI.Login.parse(response)
            cls.SESSION = result.data["cookies"]

        response = await LmsAPI.CourseList.fetch(
            cookies=cls.SESSION,
            semester=cls.SEMESTER
        )
        result = LmsAPI.CourseList.parse(response)
        course_code = list(result.data["courses"].values())[0]

        response = await LmsAPI.Attendance.fetch(cls.SESSION, course_code)
        result = LmsAPI.Attendance.parse(response)

        print(result)