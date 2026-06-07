class AppError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, errors=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.errors = errors or []


class ValidationError(AppError):
    status_code = 400


class AuthError(AppError):
    status_code = 401


class ExternalApiError(AppError):
    status_code = 502


class RouteNotFoundError(AppError):
    status_code = 404


class OptimizationError(AppError):
    status_code = 502
