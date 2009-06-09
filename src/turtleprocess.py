import sys
import multiprocessing
import code
import copy
import math
import time

from turtle import *
from vector import Vector


import wx.py.interpreter

class MyConsole(code.InteractiveConsole):
    def __init__(self,read=None,write=None,runsource_return_queue=None,*args,**kwargs):
        code.InteractiveConsole.__init__(self,*args,**kwargs)
        self.read=read
        self.write=write
        self.runsource_return_queue=runsource_return_queue
        if read is None or write is None:
            raise NotImplementedError

    def raw_input(self,prompt):
        self.write(prompt)
        return self.read()

    def write(self,output):
        return self.write(output)

    def interact(self, banner=None):
        """Closely emulate the interactive Python console.

        The optional banner argument specify the banner to print
        before the first interaction; by default it prints a banner
        similar to the one printed by the real Python interpreter,
        followed by the current class name in parentheses (so as not
        to confuse this with the real interpreter -- since it's so
        close!).

        """
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        if banner is None:
            self.write("Python %s on %s\n%s\n(%s)\n" %
                       (sys.version, sys.platform, cprt,
                        self.__class__.__name__))
        else:
            self.write("%s\n" % str(banner))
        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input(prompt)
                    # Can be None if sys.stdin was redefined
                    encoding = getattr(sys.stdin, "encoding", None)
                    if encoding and not isinstance(line, unicode):
                        line = line.decode(encoding)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    more = self.push(line)
                    self.runsource_return_queue.put(more)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0

class TurtleProcess(multiprocessing.Process):

    def __init__(self,*args,**kwargs):
        multiprocessing.Process.__init__(self,*args,**kwargs)

        self.Daemon=True

        self.input_queue=multiprocessing.Queue()
        self.output_queue=multiprocessing.Queue()
        self.runsource_return_queue=multiprocessing.Queue()



        self.turtle_queue=multiprocessing.Queue()

        """
        Constants:
        """
        self.FPS=25
        self.FRAME_TIME=1/float(self.FPS)



    def send_report(self):
        self.turtle_queue.put(self.turtle)

    def run(self):
        turtle=self.turtle=Turtle()

        def go(distance):
            if distance==0: return
            sign=1 if distance>0 else -1
            distance=copy.copy(abs(distance))
            distance_gone=0
            distance_per_frame=self.FRAME_TIME*self.turtle.SPEED
            steps=math.ceil(distance/float(distance_per_frame))
            angle=from_my_angle(turtle.orientation)
            unit_vector=Vector((math.sin(angle),math.cos(angle)))*sign
            step=distance_per_frame*unit_vector
            for i in range(steps-1):
                turtle.pos+=step
                time.sleep(self.FRAME_TIME)
                self.send_report()
                distance_gone+=distance_per_frame

            last_distance=distance-distance_gone
            last_sleep=last_distance/float(self.turtle.SPEED)
            last_step=unit_vector*last_distance
            turtle.pos+=last_step
            time.sleep(last_sleep)
            self.send_report()

        def turn(angle):
            if angle==0: return
            sign=1 if angle>0 else -1
            angle=copy.copy(abs(angle))
            angle_gone=0
            angle_per_frame=self.FRAME_TIME*self.turtle.ANGULAR_SPEED
            steps=math.ceil(angle/float(angle_per_frame))
            step=angle_per_frame*sign
            for i in range(steps-1):
                turtle.orientation+=step
                time.sleep(self.FRAME_TIME)
                self.send_report()
                angle_gone+=angle_per_frame

            last_angle=angle-angle_gone
            last_sleep=last_angle/float(self.turtle.ANGULAR_SPEED)
            last_step=last_angle*sign
            turtle.orientation+=last_step
            time.sleep(last_sleep)
            self.send_report()

        def color(color):
            #if not valid_color(color):
            #    raise StandardError(color+" is not a valid color.")
            turtle.color=color
            self.send_report()


        locals_for_console=locals() # Maybe make sure there's no junk?
        #locals_for_console.update({"go":go})

        """
        import wx; app=wx.App();
        def valid_color(color):
            return not wx.Pen(color).GetColour()==wx.Pen("malformed").GetColour()
        """


        console=MyConsole(read=self.input_queue.get,write=self.output_queue.put,
                          runsource_return_queue=self.runsource_return_queue,
                          locals=locals_for_console)
        #console=wx.py.interpreter.Interpreter
        console.interact()
        """
        while True:
            input=self.input_queue.get()
            exec(input)
        """
        pass