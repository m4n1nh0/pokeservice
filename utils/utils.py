"""Utilities methods/functions."""

import secrets
import string

from fastapi import HTTPException


class Utils:
    """Utilities classe methods/functions."""
    def __init__(self):
        """Init the class."""
        self.__return_data = None

    def get_return_data(self):
        """Get the return data."""
        return self.__return_data

    def secret_key_generator(self, total: int = 64) -> str:
        """Random string generator.

        :param total: The total number of string length
        :return: A random string
        """
        generate = string.ascii_letters + string.digits + string.punctuation
        self.__return_data = ''.join(secrets.choice(generate) for _ in range(total))
        return self.__return_data

    @staticmethod
    def api_exception(message, status, headers=None) -> HTTPException:
        """HTTP error message and status.

        :param message: Error message to api return
        :param status: HTTP status code to api return.
        :param headers: Headers to api return
        :return: String with error message and status
        """
        return HTTPException(
            status_code=status,
            detail=message,
            headers=headers
        )
