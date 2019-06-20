class EmbedException(Exception):
    pass

class EmbedTitleError(EmbedException):
    def __init__(self, message):
        self.message = message

class EmbedColorExcepton(EmbedException):
    def __init__(self, message):
        self.message = message

class EmbedFooterException(EmbedException):
    def  __init__(self, message):
        self.message=message

class EmbedImageException(EmbedException):
    def __init__(self, message):
        self.message=message
