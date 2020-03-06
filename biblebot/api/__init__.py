from .base import (
    HTTPClient,
    ResourceData,
    ErrorData,
)
from .intranet import Login as IntranetLogin
from .intranet import StudentPhoto as IntranetStudentPhoto
from .intranet import Chapel as IntranetChapel
from .intranet import Timetable as IntranetTimetable
from .intranet import Course as IntranetCourse
from .lms import Login as LmsLogin
from .lms import Profile as LmsProfile
from .lms import CourseList as LmsCourseList
from .lms import Attendance as LmsAttendance
from .kbu import MainNotice as KbuMainNotice
from .kbu import ScholarshipNotice as KbuScholarshipNotice
from .kbu import IllipNotice as KbuIllipNotice
from .mileage import Login as MileageLogin
from .mileage import Search as MileageSearch
from .mileage import Statement as MileageStatement
from ._mileage import SearchParamData as MileageSearchParamData
from ._mileage import StatementParamData as MileageStatementParamData


__all__ = (
    "HTTPClient",
    "ResourceData",
    "ErrorData",
    "IntranetAPI",
    "LmsAPI",
    "KbuAPI",
    "MileageAPI",
    "MileageParam",
)


class IntranetAPI:
    Login = IntranetLogin
    StudentPhoto = IntranetStudentPhoto
    Chapel = IntranetChapel
    Timetable = IntranetTimetable
    Course = IntranetCourse


class LmsAPI:
    Login = LmsLogin
    Profile = LmsProfile
    CourseList = LmsCourseList
    Attendance = LmsAttendance


class KbuAPI:
    MainNotice = KbuMainNotice
    ScholarshipNotice = KbuScholarshipNotice
    IllipNotice = KbuIllipNotice


class MileageAPI:
    Login = MileageLogin
    Search = MileageSearch
    Statement = MileageStatement


class MileageParam:
    SearchParamData = MileageSearchParamData
    StatementParamData = MileageStatementParamData
