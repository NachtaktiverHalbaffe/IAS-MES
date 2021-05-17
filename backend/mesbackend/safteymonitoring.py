"""
Filename: safteymonitoring.py
Version name: 0.1, 2021-05-17
Short description: Module for error handling and for monitoring saftey constraints

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from mesapi.models import Error


class SafteyMonitoring(object):
    def __init__(self):
        self.LEVEL_WARNING = "[WARNING]"
        self.LEVEL_ERROR = "[ERROR]"
        self.LEVEL_CRITICIAL = "[CRITICAL]"

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
        error = Error
        error.level = errorLevel
        error.category = errorCategory
        error.msg = msg

        # When error is of category warning it will automatically be marked as solved
        if errorLevel == self.LEVEL_WARNING:
            error.isSolved = True
        else:
            error.isSolved = False

        error.save()

    # Gets executed when a error is saved. It analyses the error and decides what the system has to do
    # to solve the error

    def handleError(error):
        pass
