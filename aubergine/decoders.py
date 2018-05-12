"""Various decoders used to extract content from request."""
import json
from aubergine.common import Loggable


class DecodingError(Exception):
    """An error raised when decoding fails."""

    def __init__(self, msg):
        super(DecodingError, self).__init__(msg)
        self.msg = msg


class PlainDecoder(Loggable):
    """Dummy decoder needed to be plugged in for simple parameters."""

    @staticmethod
    def decode(content):
        """Decode given string.

        This in an identity map.
        """
        return content


class JSONDecoder(Loggable):
    """Decoder for JSON content type.

    This is basically an adapter to Python's json.loads that raises
    DecodingError on decoding failure.
    """

    def decode(self, content):
        """Decode given JSON string.

        :param content: content to be decoded
        :type content: str or bytes
        :returns: mapping with data decoded from content
        :rtype: dict:
        :raises DecodingError: if content is not a valid JSON.
        """
        try:
            return json.loads(content)
        except json.JSONDecodeError as err:
            self.logger.exception('Decoding failed.')
            raise DecodingError(err.msg)
