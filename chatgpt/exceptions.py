class APIClientException(Exception):
    pass


class StatusCodeException(APIClientException):
    pass


class InvalidResponseException(APIClientException):
    pass


class UnauthorizedException(APIClientException):
    pass


class ForbiddenException(APIClientException):
    pass
