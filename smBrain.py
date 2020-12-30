import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

class MySMClass(sm.SM):
    coeff = 5
    fvelMax = 0.3
    tolerance = 0.001

    def __init__(self, targetDist):
        self.targetDist = targetDist
        self.startState = 5

    def getNextValues(self, state, inp):
        currentDist = min(inp.sonars[3], inp.sonars[4])
        delta = currentDist - self.targetDist

        if abs(delta) > self.tolerance:
            fvel = self.coeff * delta * self.fvelMax
            fvel = max(min(fvel, self.fvelMax), -self.fvelMax)
            return (currentDist, io.Action(fvel = fvel, rvel = 0))
        else:
            return (currentDist, io.Action(fvel = 0, rvel = 0))

    
    # def done(self, state):
        # return abs(state - self.targetDist) <= self.tolerance

mySM = MySMClass(0.5)
mySM.name = 'brainSM'

######################################################################
###
###          Brain methods
###
######################################################################

def plotSonar(sonarNum):
    robot.gfx.addDynamicPlotFunction(y=('sonar'+str(sonarNum),
                                        lambda: 
                                        io.SensorInput().sonars[sonarNum]))

# this function is called when the brain is (re)loaded
def setup():
    robot.gfx = gfx.RobotGraphics(drawSlimeTrail=True, # slime trails
                                  sonarMonitor=False) # sonar monitor widget
    
    # set robot's behavior
    robot.behavior = mySM

# this function is called when the start button is pushed
def brainStart():
    robot.behavior.start(traceTasks = robot.gfx.tasks())

# this function is called 10 times per second
def step():
    inp = io.SensorInput()
    print inp.sonars[3]
    robot.behavior.step(inp).execute()
    io.done(robot.behavior.isDone())

# called when the stop button is pushed
def brainStop():
    pass

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
