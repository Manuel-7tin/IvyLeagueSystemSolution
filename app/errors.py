class UserNotFoundError(Exception):
    """
    Custom exception for handling improperly structured files.
    Raised when a file does not follow the expected format.
    """

    def __init__(self, message="User not found lil bro."):
        """
        Initializes the exception with a default or custom error message.
        Args:
            message (str, optional): The error message to display. Defaults to a casual phrasing.
        """
        super().__init__(message)