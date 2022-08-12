class Error(Exception):
    """Base class for other exceptions"""

class TrackerPreviouslyRegistered(Error):
    """Exception raised when API request returns that tracker is already registered."""
    def __init__(self, tracking_number, message="Tracking API returned that tracking number is already registered."):
        self.tracking_number = tracking_number
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "{} -> {}".format(self.tracking_number, self.message)

class TrackerRejectedUnknownCode(Error):
    """Exception raised when API request rejects a tracker with an unrecognized error code."""
    def __init__(self, tracking_number, code, message="Tracking API returned an unrecognized error code."):
        self.tracking_number = tracking_number
        self.error_code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return "{} -> {}: {}".format(self.tracking_number, self.message, self.error_code)