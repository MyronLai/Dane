class EmbedException(Exception):
    pass

class EmbedTitleError(EmbedException):
    def __init__(self, message):
        self.message = message