from HiggsAnalysis.CombinedLimit.PhysicsModel import *

class HighMass( PhysicsModel ):
    ''' Model used to unfold differential distributions for Fiducial cross-section model for both H->4l and Z->4l'''

    def __init__(self):
        PhysicsModel.__init__(self)
        self.sigmaRange=[0.,300.0]
        self.nBin=4
        self.defaultMH=800.0
        self.debug=1

    def setPhysicsOptions(self,physOptions):
        if self.debug>0:print "Setting PhysicsModel Options"
        for po in physOptions:
            if po.startswith("range="):
                self.sigmaRange=po.replace("range=","").split(",")
                if len(self.sigmaRange)!=2:
                    raise RunTimeError, "sigmaRange require minimal and maximal values: range=min,max"
                if self.debug>0:print "New sigmaRange is ", self.sigmaRange
            if po.startswith("mass="):
                self.defaultMH=float( po.replace('mass=','') )
            #verbose
            if po.startswith("verbose"):
                self.debug = 1


    def doParametersOfInterest(self):
        POIs=""
        if self.debug>0:print "Setting pois"

        if self.modelBuilder.out.var("sigma"):
            self.modelBuilder.out.var("sigma").setRange(float(self.sigmaRange[0]), float(self.sigmaRange[1]))
            self.modelBuilder.out.var("sigma").setConstant(False)
        else :
            self.modelBuilder.doVar("sigma[1, %s,%s]" % (float(self.sigmaRange[0]),float(self.sigmaRange[1])))

        POIs+="sigma"
        if self.debug>0:print "Added sigma to the POIs"

        if self.modelBuilder.out.var("MH"):
            print 'MH will be assumed to be', self.defaultMH
            self.modelBuilder.out.var("MH").removeRange()
            self.modelBuilder.out.var("MH").setVal(self.defaultMH)
        else:
            print 'MH (not there before) will be assumed to be', self.defaultMH
            self.modelBuilder.doVar("MH[%g]" % self.defaultMH)

        print POIs

        self.modelBuilder.doSet("POI",POIs)
        self.setup()

    def setup(self):        
        self.modelBuilder.factory_('expr::sigmaXbr("@0", sigma)')

    def getYieldScale(self,bin,process):
        if not self.DC.isSignal[process]: return 1
        Processes = []                
        for channel in ['ggH_hzz', 'qqH_hzz']:       
            Processes += [channel]
        if process in Processes: return 'sigmaXbr'
        else: return 1

highMass=HighMass()
