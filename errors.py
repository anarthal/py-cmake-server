
class CmakeError(Exception):
    pass

class CommunicationError(CmakeError):
    pass

class ErrorReply(CmakeError):
    pass