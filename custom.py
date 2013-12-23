#!/usr/bin/env python2.7

import json

class doubleQuoteDict(dict):
    def __str__(self):
        return json.dumps(self)

    def __repr__(self):
        return json.dumps(self)
