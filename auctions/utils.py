import random
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


LIGHTSTEELBLUE = '#B0C4DE'
LIGHTSKYBLUE = '#87CEFA'
SKYBLUE = '#87CEEB'
LIGTHBLUE = '#ADD8E6'
POWDERBLUE = '#B0E0E6'
LIGHTCYAN = '#E0FFFF'
PALETURQUOISE = '#AFEEEE'
AQUAMARINE = '#66CDAA'
LIGTHSEAGREEN = '#20B2AA'

BG_COLOURS = (
    (LIGHTSTEELBLUE, 'Light Steel Blue'),
    (LIGHTSKYBLUE, 'Light Sky Blue'),
    (SKYBLUE, 'Sky Blue'),
    (LIGTHBLUE, 'Light Blue'),
    (POWDERBLUE, 'Powder Blue'),
    (LIGHTCYAN, 'Light Cyan'),
    (PALETURQUOISE, 'Pale Turquoise'),
    (AQUAMARINE, 'Aquamarine'),
    (LIGTHSEAGREEN, 'Light Sea Green'),
)


def get_random_colour():
    return random.choice(BG_COLOURS)[0]
