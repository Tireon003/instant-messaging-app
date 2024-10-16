class NoSuchUserInDBException(Exception):
    pass


class WrongPasswordException(Exception):
    pass


class UserAlreadyExistException(Exception):
    pass


class InvalidCodeException(Exception):
    pass
