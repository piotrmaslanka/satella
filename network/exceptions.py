class NetworkException(Exception):
    """Root class for network exceptions"""

class DataUnavailableException(NetworkException):
    """Cannot satisfy request due to lack of data"""
class ConnectionFailedException(NetworkException):
    """Operation cannot be completed because underlying implementation reported an error"""