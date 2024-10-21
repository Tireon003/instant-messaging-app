import base64


def create_activation_code(payload: str) -> str:
    """
    Method creating activation code using base64 encoding
    :param payload: user registration schema
    :return: string of activation code
    """

    base64_code_bytes = base64.b64encode(payload.encode('utf-8'))
    base64_code_str = base64_code_bytes.decode('utf-8')
    return base64_code_str
