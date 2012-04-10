#
# Copyright (c) 2011 All Rights Reserved, Byer Capital, LLC
#
# @author: ianbyer
#

class ConnectorError(Exception):
    def __init__(self, type, message):
        Exception.__init__(self, message)
        self.type = type  