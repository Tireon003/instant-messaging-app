import aiohttp


class AuthApi:

    @staticmethod
    async def complete_user_registration(code: str, tg_chat_id) -> bool:
        """
        Method for completing user registration
        :param code: Code for user registration which bot gets from user
        :param tg_chat_id: Chat id of user and bot conversation
        :return: Boolean value: True if got status 201, False otherwise
        """
        async with aiohttp.ClientSession() as session:
            params = [("code", code), ("tg_chat_id", tg_chat_id)]
            url = f"http://api_server:8777/api/auth/activate_registration_code"
            async with session.post(url, params=params) as response:
                if response.status == 201:
                    return True
                return False

    @staticmethod
    async def check_if_chat_id_binded(chat_id: int) -> bool:
        """
        Method for checking if chat id is binded. If chat id is binded,
        returns True
        :param chat_id: id of tg chat needed for checking
        :return: Boolean value: True if got status 200, False otherwise
        """
        async with aiohttp.ClientSession() as session:
            params = [("tg_chat_id", chat_id)]
            url = f"http://api_server:8777/api/auth/check_if_tg_is_binded"
            async with session.get(url, params=params) as response:
                return response.status == 200
