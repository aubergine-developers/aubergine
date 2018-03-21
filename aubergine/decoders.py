"""Various decoders used to extract content from request."""


class ParameterValidationError(ValueError):
    """An error raised when some parameter value failed to validate."""
    def __init__(self, validation_errors):
        super(ParameterValidationError, self).__init__(validation_errors)
        self.errors = validation_errors
