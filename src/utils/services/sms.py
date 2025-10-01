from sms_ir import SmsIr


class SMS:
    def __init__(self):
        api_key: str = ""
        linenumber: str = ""
        sms_ir = SmsIr(api_key, linenumber)

    @staticmethod
    def send_sms(self, number, message):
        self.sms_ir.send_sms(number, message)

    @staticmethod
    def send_verify(self, number, template_id, parameters):
        self.sms_ir.send_verify_code(number, template_id, parameters)
