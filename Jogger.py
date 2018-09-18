# $Id$
#
# Author: Andreas Bockert
# Date: 15-Aug-2018

import sys
import os

if __name__ == "__main__":
    PRGPATH=os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.join(PRGPATH, 'lib'))
    sys.path.append(os.path.join(PRGPATH, 'plugins'))

import math
import time
import threading

from CNC import CNC
import Sender

class Gamepad:
    def __init__(self):
        import inputs
        self.get_gamepad = inputs.get_gamepad
        self.x = 0.
        self.y = 0.
        self.z = 0.

        self.button = {}
        for c, s in inputs.KEYS_AND_BUTTONS:
            self.button[s] = False
        
        # Calibration of sensitivity of axes:
        # inputs in range r[0]..r[1] maps to -1..0
        # inputs in range r[1]..r[2] maps to  0
        # inputs in range r[2]..r[3] maps to  0..1
        self.x_range = [0, 112, 144, 255]
        self.y_range = [0, 112, 144, 255]
        self.z_range = [0, 112, 144, 255]

    def __str__(self):
        return "x %.2f y %.2f z %.2f" % (self.x, self.y, self.z)

    def _remap(self, v, r):
        if v < r[1]:
            v = (float(v) - r[1]) / (r[1] - r[0])
        elif v < r[2]:
            v = 0.
        else:
            v = (float(v) - r[2]) / (r[3] - r[2])

        if v < -1.0:
            return -1.0
        elif v < 1.0:
            return v
        else:
            return 1.0
    
    def _abs_x(self, x):
        self.x = self._remap(x, self.x_range)

    def _abs_y(self, y):
        self.y = self._remap(y, self.y_range)

    def _abs_z(self, z):
        self.z = self._remap(z, self.z_range)

    def _handle_absolute(self, code, state):
        if code == 'ABS_X':
            self._abs_x(state)
        elif code == 'ABS_Y':
            self._abs_y(state)
        elif code == 'ABS_Z':
            self._abs_z(state)
        else:
            print(code, state)
        
    def _handle_key(self, key_str, key_state):
        self.button[key_str] = key_state != 0

    def processEvents(self):
        for k in range(10):
            events = self.get_gamepad()
            if not events:
                return;
            
            for e in events:
                if e.ev_type == 'Sync':
                    pass
                elif e.ev_type == 'Absolute':
                    self._handle_absolute(e.code, e.state)
                elif e.ev_type == 'Key':
                    self._handle_key(e.code, e.state)
                elif e.ev_type == 'Misc':
                    pass # Squash.
                else: # For now, print unexpected events.
                    print(e.ev_type, e.code, e.state)

class GamepadThread(threading.Thread):
    def __init__(self, gp):
        threading.Thread.__init__(self)
        self.gp = gp
        self.alive = False

    def run(self):
        while self.alive:
            self.gp.processEvents()
        
    def start(self):
        self.alive = True
        threading.Thread.start(self)
            
    def stop(self):
        self.alive = False
        self.join()
                    
class Jogger:
    __doc__ = _("Jogging")
    
    def __init__(self, app):
        self.app = app
        self.update_interval = 50
        self.default_feedrate = 10000
        self._gamePad_thread = None
        self._gamePad = None
        self._moving = False

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

    def _gamePadPoll(self):
        if not self._gamePad:
            return

        if self._gamePad.x != 0 or self._gamePad.y != 0:
            l = 10
            delta = (l*self._gamePad.x, -l*self._gamePad.y, 0) #self._gamePad.z)
            self.jogDelta(delta)
            self._moving = 1
            print str(self._gamePad)
        else:
            if self._moving:
                self.jogCancel()
                self._moving = False
                          
        self.app.after(self.update_interval, self._gamePadPoll)
        self.app.protocol("WM_DELETE_WINDOW", self.disableGamepadJogging)
        
    def enableGamepadJogging(self):
        if not self._gamePad:
            try:
                self._gamePad = Gamepad()
                self._gamePad_thread = GamepadThread(self._gamePad)
                self._gamePad_thread.start()
            except:
                print "Failed to create gamepad."
                self._gamePad = None
                self._gamePad_thread = NOne
                return False

        # Call poll to start timer.
        self._gamePadPoll();
            
        return True

    def disableGamepadJogging(self):
        if self._gamePad_thread:
            self._gamePad_thread.stop()
        self._gamePad_thread = None
        self._gamePad = None

if __name__ == "__main__":
    gp = Gamepad()
    t = GamepadThread(gp)
    t.start()
    t0 = time.time()
    while time.time() - t0 < 30:
        print "%f" % gp.x
        time.sleep(1)
    t.stop()

    
    
