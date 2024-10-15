import bcrypt


class HashingTool:

    @staticmethod
    def encrypt(password: str) -> str:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('ascii')

    @staticmethod
    def verify(provided_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(provided_password.encode("utf-8"), hashed_password.encode("ascii"))
