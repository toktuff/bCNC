# $Id$
#
# Author: 
# Date: 15-Aug-2018

import math

from CNC import CNC
import Sender

class Jogger:
    __doc__ = _("Jogging")
    
    def __init__(self, app):
        self.app = app
        self.default_feedrate = 10000

    def jogDir(self, direction, feedrate = None):
        if not feedrate:
            feedrate = self.default_feedrate
        l = math.sqrt(direction[0]*direction[0] +
                      direction[1]*direction[1])
        normalized = (direction[0] / l, direction[1] / l)
        self.sendGCode("$J=G91G21X1F%d"%(int(feedrate)))
