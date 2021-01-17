
import logging


class RequestLogger(object):
    """
    Helper class to format request logging in a standard way, on top of the
    other logging provided in setup.

    User id is embedded into every log message, which makes it convenient to
    track a user as they navigate the site by grepping into the logs e.g.
    ```bash
        grep auctions.log | grep '| User: 1'
    ```

    One exception to user id is when someone attempts to log in with an invalid
    user name, where the attempted user name will be logged in place of the id.
    """

    def __init__(self, name):
        self._logger = logging.getLogger(name)

    def debug(self, uid, message):
        self._logger.debug(f'User: {uid} > {message}')

    def info(self, uid, message):
        self._logger.info(f'User: {uid} > {message}')

    def warning(self, uid, message):
        self._logger.warning(f'User: {uid} > {message}')

    def error(self, uid, message):
        self._logger.error(f'User: {uid} > {message}')

    def critical(self, uid, message):
        self._logger.critical(f'User: {uid} > {message}')
