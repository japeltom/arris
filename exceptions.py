class ConfigError(Exception):
    """Exception class for errors while reading configuration."""

    def __init__(self, message):
        super().__init__()
        self.message = message

    def __str__(self):
        return message

class EXIFReadError(Exception):
    """Exception class for errors while reading EXIF metadata."""

    def __init__(self, filename, message):
        super().__init__()
        self.filename = filename
        self.message = message

    def __str__(self):
        return "While reading EXIF metadata from file '{}', the following error occurred: '{}'.".format(self.filename, self.message)

class EXIFWriteError(Exception):
    """Exception class for errors while writing EXIF metadata."""

    def __init__(self, filename, message):
        super().__init__()
        self.filename = filename
        self.message = message

    def __str__(self):
        return "While writing EXIF metadata to file '{}', the following error occurred: '{}'.".format(self.filename, self.message)


class XMPReadError(Exception):
    """Exception class for errors while reading XMP metadata."""

    def __init__(self, filename, message):
        super().__init__()
        self.filename = filename
        self.message = message

    def __str__(self):
        return "While reading XMP metadata from file '{}', the following error occurred: '{}'.".format(self.filename, self.message)

class XMPWriteError(Exception):
    """Exception class for errors while writing XMP metadata."""

    def __init__(self, filename, message):
        super().__init__()
        self.filename = filename
        self.message = message

    def __str__(self):
        return "While writing XMP metadata to file '{}', the following error occurred: '{}'.".format(self.filename, self.message)

