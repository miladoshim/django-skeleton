from rest_framework.exceptions import APIException


class InvalidFileException(APIException):
    status_code = 400
    default_detail = "Invalid file format"
    default_code = "invalid file format"


class FileSizeExceededException(APIException):
    status_code = 400
    default_detail = "File size exceeds limit"
    default_code = "file size exceeds limit"


class FileUploadException(APIException):
    status_code = 400
    default_detail = "File upload failed"
    default_code = "file upload failed"
