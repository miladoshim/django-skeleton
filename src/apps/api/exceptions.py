from rest_framework.exceptions import APIException

class UploadFailedException(APIException):
    status_code = 400
    default_detail = "Unable to uploading file"
    default_code = "unable to uploading file"