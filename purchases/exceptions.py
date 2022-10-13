class Error(Exception):
    """Base class for other exceptions"""

    def __init__(self, message="Generic error"):
        self.message = message
        super().__init__(self.message)


class TrackerPreviouslyRegistered(Error):
    """Exception raised when API request returns that tracker is already registered."""

    def __init__(
        self,
        tracking_number,
        message="Tracking API returned that tracking number is already registered.",
    ):
        self.tracking_number = tracking_number
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.tracking_number} -> {self.message}"


class TrackerReturnedMultipleCarriers(Error):
    """Exception raised with tracker returns more than one carrier."""

    def __init__(
        self,
        tracking_number,
        carrier_count,
        message="Tracker returned multiple possible carriers.",
    ):
        self.tracking_number = tracking_number
        self.message = message
        self.carrier_count = carrier_count
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"Tracker returned {self.carrier_count} carriers."


class TrackerRejectedUnknownCode(Error):
    """Exception raised when API request rejects a tracker
    with an unrecognized error code.
    """

    def __init__(
        self,
        tracking_number,
        code,
        message="Tracking API returned an unrecognized error code.",
    ):
        self.tracking_number = tracking_number
        self.error_code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "{} -> {}: {}".format(
            self.tracking_number, self.message, self.error_code
        )


class StatusCodeNotFound(Error):
    """Exception raised when status two-character code not found"""

    def __init__(self, code, message="No matching status found. Please verify code."):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"'{self.code}': {self.message}"
