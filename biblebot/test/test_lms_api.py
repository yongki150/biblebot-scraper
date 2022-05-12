from aiounittest import AsyncTestCase

from biblebot.api import LmsAPI


class Test(AsyncTestCase):
    # Enter your info
    USERNAME: str = ""
    PASSWORD: str = ""

    # Assign later
    COOKIES: str = ""
    SEMESTER: str = "20221"
    COURSE_CODE: str = ""

    def setUp(self) -> None:
        print("\n")

    def tearDown(self) -> None:
        print()

    @classmethod
    async def test_login_scraper(cls):
        response = await LmsAPI.Login.fetch(cls.USERNAME, cls.PASSWORD)
        result = LmsAPI.Login.parse(response)
        cls.COOKIES = result.data["cookies"]

        print(result)

    @classmethod
    async def test_profile_scraper(cls):
        response = await LmsAPI.Profile.fetch(cls.COOKIES)
        result = LmsAPI.Profile.parse(response)

        print(result)

    @classmethod
    async def test_course_list_scraper(cls):
        response = await LmsAPI.CourseList.fetch(cls.COOKIES, cls.SEMESTER)
        result = LmsAPI.CourseList.parse(response)
        cls.COURSE_CODE = list(result.data["courses"].values())[0]

        print(result)

    @classmethod
    async def test_attendance_scraper(cls):
        response = await LmsAPI.Attendance.fetch(cls.COOKIES, cls.COURSE_CODE)
        result = LmsAPI.Attendance.parse(response)

        print(result)