class ConfigError(Exception):
    """Exception class for errors while reading configuration."""

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message

class EXIFReadError(Exception):
    """Exception class for errors while reading EXIF metadata."""

    def __init__(self, file_name, message):
        super().__init__()
        self.file_name = file_name
        self.message = message

    def __str__(self):
        return f"While reading EXIF metadata from file '{self.file_name}', the following error occurred: '{self.message}'."

class EXIFWriteError(Exception):
    """Exception class for errors while writing EXIF metadata."""

    def __init__(self, file_name, message):
        super().__init__()
        self.file_name = file_name
        self.message = message

    def __str__(self):
        return f"While writing EXIF metadata to file '{self.file_name}', the following error occurred: '{self.message}'."


class XMPReadError(Exception):
    """Exception class for errors while reading XMP metadata."""

    def __init__(self, file_name, message):
        super().__init__()
        self.file_name = file_name
        self.message = message

    def __str__(self):
        return f"While reading XMP metadata from file '{self.file_name}', the following error occurred: '{self.message}'."

class XMPWriteError(Exception):
    """Exception class for errors while writing XMP metadata."""

    def __init__(self, file_name, message):
        super().__init__()
        self.file_name = file_name
        self.message = message

    def __str__(self):
        return f"While writing XMP metadata to file '{self.file_name}', the following error occurred: '{self.message}'."

