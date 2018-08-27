# $Id$
#
# Author: Andreas Bockert
# Date: 15-Aug-2018

import math

from CNC import CNC
import Sender

class Jogger:
    __doc__ = _("Jogging")
    
    def __init__(self, app):
        self.app = app
        self.default_feedrate = 10000

    def sendGCode(self, cmd):
        self.app.sendGCode(cmd)

    def jogDir(self, direction, feedrate = None):
        feedrate = feedrate or self.default_feedrate
        l = math.sqrt(direction[0]*direction[0] +
                      direction[1]*direction[1])
        normalized = (direction[0] / l, direction[1] / l)
        self.sendGCode("$J=G91G21X1F%d"%(int(feedrate)))

    def jogDelta(self, delta, feedrate = None):
        feedrate = feedrate or self.default_feedrate
        feedrate = float(feedrate)
        delta = [float(x) for x in delta]
        cmd = "$J=G91G21X%fY%fZ%fF%f" % (delta[0], delta[1], delta[2], feedrate)
        self.sendGCode(cmd)

    def jogCancel(self):
        self.app.jogCancel()

