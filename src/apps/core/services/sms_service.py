from django.conf import settings
from kavenegar import APIException, HTTPException, KavenegarAPI


class Kavenegar:
    def __init__(self) -> None:
        pass

    def send_sms(receptor, message):
        try:
            api = KavenegarAPI(
                settings.KAVENEGAR_API_KEY,
            )
            params = {
                "sender": settings.KAVENEGAR_SENDER,
                "receptor": receptor,
                "message": message,
            }
            response = api.sms_send(params)
            print(response)
        except APIException as e:
            print(e)
        except HTTPException as e:
            print(e)

    def send_otp(receptor, otp):
        try:
            api = KavenegarAPI(
                settings.KAVENEGAR_API_KEY,
            )
            params = {
                "template": settings.KAVENEGAR_OTP_TEMPLATE,
                "receptor": receptor,
                "token": otp,
                "type": "sms",
            }
            response = api.verify_lookup(params)
            return True

        except APIException as e:
            print("------------------Api Err----------------------------------")
            print(e)
            return False
        except HTTPException as e:
            print("-------------------HTTP Err-----------------------------------")
            print(e)
            return False

    def send_bulk(self, sender=[], receptor=[], message=[]):
        try:
            api = KavenegarAPI(
                settings.KAVENEGAR_API_KEY,
            )
            params = {
                "sender": '["",""]',
                "receptor": '["",""]',
                "message": '["",""]',
            }
            response = api.sms_sendarray(params)
            print(response)
        except APIException as e:
            print(e)
        except HTTPException as e:
            print(e)


def send_sms(receptor, message: str):
    return Kavenegar.send_sms(receptor, message)


def send_otp(receptor, otp):
    return Kavenegar.send_otp(receptor, otp)
