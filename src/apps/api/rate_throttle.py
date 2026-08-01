from rest_framework.throttling import UserRateThrottle


class ThenPerMinuteThrottle(UserRateThrottle):
    rate = "10/minute"
