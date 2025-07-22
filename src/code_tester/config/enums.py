from enum import IntEnum


class ExitCode(IntEnum):
    SUCCESS = 0
    TESTS_FAILED = 1
    FILE_NOT_FOUND = 2
    JSON_ERROR = 3
    UNEXPECTED_ERROR = 10