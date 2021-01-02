import math
import lib601.util as util
import lib601.sm as sm
import lib601.gfx as gfx
from soar.io import io

class MySMClass(sm.SM):
    fcoeff = 10
    rcoeff = 500
    fvelMax = 0.3
    rvelMax = 0.3
    tolerance = 0.0001

    def __init__(self, targetDist):
        self.targetDist = targetDist
        self.startState = 'searching' # searching, following

    def greaterThan(self, d1, d2):
        return d1 - d2 > self.tolerance

    def lessThan(self, d1, d2):
        return d1 - d2 < -self.tolerance

    def equals(self, d1, d2):
        return abs(d1 - d2) <= self.tolerance

    def calculateFvel(self, delta):
        fvel = self.fcoeff * delta * self.fvelMax
        fvel = max(min(fvel, self.fvelMax), -self.fvelMax)
        return fvel

    def calculateRvel(self, delta):
        rvel = self.rcoeff * delta * self.rvelMax
        rvel = max(min(rvel, self.rvelMax), -self.rvelMax)
        return rvel

    def stepForward(self, delta):
        fvel = self.calculateFvel(delta)
        return io.Action(fvel = fvel, rvel = 0)

    def stepCCW(self, delta):
        rvel = self.calculateRvel(abs(delta))
        return io.Action(fvel = self.targetDist / 10, rvel = rvel)

    def stepCW(self, delta):
        rvel = self.calculateRvel(-abs(delta))
        return io.Action(fvel = self.targetDist / 10, rvel = rvel)

    def getDelta(self, sonar):
        delta = sonar - self.targetDist
        return delta

    def getSteerAwayDelta(self, inp):
        for sonar in inp.sonars[3:]:
            if self.lessThan(sonar, self.targetDist):
                return self.getDelta(sonar)

    def getSteerToDelta(self, inp):
        sonar = inp.sonars[7]
        if self.greaterThan(sonar, self.targetDist):
            return self.getDelta(sonar)

    def getNextValues(self, state, inp):
        forwardDist = min(inp.sonars[3], inp.sonars[4])
        wallDist = inp.sonars[7]
        if state == 'searching':
            delta = forwardDist - self.targetDist

            if abs(delta) > self.tolerance:
                return (state, self.stepForward(delta))
            else:
                return ('following', io.Action(fvel = 0, rvel = 0))

        if state == 'following':
            steerAwayDelta = self.getSteerAwayDelta(inp)
            print '1-', steerAwayDelta
            if steerAwayDelta is not None:
                delta = forwardDist - self.targetDist
                return (state, self.stepCCW(delta))

            steerToDelta = self.getSteerToDelta(inp)
            print '2-', steerToDelta
            if steerToDelta is not None:
                delta = wallDist - self.targetDist
                return (state, self.stepCW(delta))

            return (state, self.stepForward(0.1))


        return (state, io.Action(fvel = 0, rvel = 0))

    
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
    # print inp.sonars[3]
    robot.behavior.step(inp).execute()
    io.done(robot.behavior.isDone())

# called when the stop button is pushed
def brainStop():
    pass

# called when brain or world is reloaded (before setup)
def shutdown():
    pass
