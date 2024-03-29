"""
Filename: safteymonitoring.py
Version name: 1.0, 2021-07-10
Short description: Module for error handling and for monitoring saftey constraints

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


class SafteyMonitoring(object):
    def __init__(self):
        # Constant for level
        self.LEVEL_WARNING = "[WARNING]"
        self.LEVEL_ERROR = "[ERROR]"
        self.LEVEL_CRITICIAL = "[CRITICAL]"
        # Constant for categories
        self.CATEGORY_CONNECTION = "Connection issue"
        self.CATEGORY_INPUT = "Invalid input"
        self.CATEGORY_OPERATIONAL = "Operational issue"
        self.CATEGORY_DATA = "Data Integrity & Consistency issue"
        self.CATEGORY_UNKOWN = "Unknown issue"

    # Gets an error of an component. This method saves it to an Error object
    # @params:
    # errorLevel: Level of the error. Either [WARNING], [ERROR] or [CRITICAL]
    # errorCategory: Category of the error. Either Connection issues, Invalid input,
    #                Operational issue, Integrity & Consistency issue ord Unkown
    # msg: message of the error
    def decodeError(self, errorLevel, errorCategory, msg):
        from mesapi.models import Error

        level = errorLevel
        category = errorCategory
        msg = msg
        isSolved = False
        # When error is of category warning it will automatically be marked as solved
        if errorLevel == self.LEVEL_WARNING:
            isSolved = True
        else:
            isSolved = False
        error = Error()
        error.level = level
        error.category = category
        error.msg = msg
        error.isSolved = isSolved
        error.save()

    """
    handleErrors() is defined in signals.py
    """
