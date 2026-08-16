import numpy as np
cimport numpy as np
import math
cimport cython

np.import_array()

def Attnfunction(xgrid, ygrid, scale1, scale2):
    t = (xgrid**2 + ygrid**2) 
    z1 = -np.exp(-0.5 * t * scale1) 
    z2 =  2 * np.exp(-0.5 * t *scale2)
    return z1+z2

def RFfunction(xgrid, ygrid, scale):
    t   = (xgrid**2 + ygrid**2) 
    return np.exp(-0.5 * t *scale)

DTYPE = np.int64
ctypedef np.int64_t DTYPE_t

@cython.boundscheck(False) # turn off bounds-checking for entire function
@cython.wraparound(False)  # turn off negative index wrapping for entire function
def runTrial(list visualObjects, list stimulusTypes, int steps, np.ndarray[double, ndim=3] videoinput, int xDim = 27, int yDim=27, int NNMask=3, int t1onset = 100-1, *args):
    
    cdef float dt_vm = .015
    cdef float dt_vm_IG= 0.04
    cdef float dt_vm_II = .0025 
    cdef float EE_EEG= 65.
    cdef float EE = 30. 
    cdef float EL= 0.
    cdef float EI = -10.
    cdef float AMFloorval = 0.
    cdef float AMCeilval = 30.
    cdef float LV_1Decider = 0
    cdef float individuation= .2
    cdef float LV_2Decider= 0.
    cdef float AMnoise = 0.
    cdef float AMexcitebias = .2
    cdef float LV_1excitebias = 0.
    cdef float EVsalInput = 1.
    cdef float LAI = .45 # strength of localized inhibLVion in the AM
    cdef float ThreshLV_II = 0. #threshold when LV II neurons begin inhibLVing their buddy LV neurons
    cdef float Thresh = 14. # this was 11 %threshold for attentional amplification
    cdef float ThreshIG = 8. 
    cdef float attentionweight = 2. #magnLVude of attentional amplification
    cdef float EVthresh = 7. 
    cdef float LVthresh = 5. 
    cdef float AM_highthresh = 8 

    cdef float AMtoIG_inhib =.25 #this is the coefficient for inhibLVion coming from the single buddy AM neuron
    cdef float AMtoIG_excite =.4 
    cdef float LVtoII = .02 #this is the excLVation from LV to II neurons of the same map
    cdef float ILVoLV = 6.5 #inhibLVion of II onto LV's buddy LV neuron
    cdef float MaxLVtoIG = 0.35 #this is the maximum amount that the LV neurons can excite IG neurons
    cdef float MaxAMtoIG = 0.35 #this is the maximum amount that the AM neurons can excite IG neurons

    # MAP INDICES
    cdef int excite = 0
    cdef int inhib = 1
    cdef int leak = 2

    cdef int excite_LV = 0
    cdef int exciteEEG = 3
    cdef int excite_AM = 3

    cdef np.ndarray[np.int64_t, ndim=1] xx = np.arange(-xDim, xDim+1,1)
    cdef np.ndarray[np.int64_t, ndim=1] yy = np.arange(-yDim, yDim+1,1)
    cdef np.ndarray[np.int64_t, ndim=2] xgrid, ygrid
    xgrid, ygrid = np.meshgrid(xx, yy)
    cdef np.ndarray[np.double_t, ndim=2] sombrero
    sombrero = Attnfunction(xgrid, ygrid, .07, individuation)

    cdef int RFsize = 1
    cdef np.ndarray[np.double_t, ndim=2] Gaus_RF0 = RFfunction(xgrid, ygrid, RFsize)
    cdef np.ndarray[np.double_t, ndim=2] Gaus_RF = Gaus_RF0/(Gaus_RF0.max())

    # Loop variables
    cdef int xi, yi, xk, yk, xmin, xmax, ymin, ymax, xdiff, ydiff, x2, y2
    cdef int prev=0

    cdef int visObjsCount = len(visualObjects)
    cdef np.ndarray[DTYPE_t, ndim=1] x = np.zeros(visObjsCount).astype(int)
    cdef np.ndarray[DTYPE_t, ndim=1] y = np.zeros(visObjsCount).astype(int)
    cdef np.ndarray[DTYPE_t, ndim=1] Stype = np.zeros(visObjsCount).astype(int)
    cdef np.ndarray[np.float64_t, ndim=1] onset = np.zeros(visObjsCount).astype(float) # Change to double
    cdef np.ndarray[np.float64_t, ndim=1] period = np.zeros(visObjsCount).astype(float) # Change to double

    cdef np.ndarray[np.float64_t, ndim=1] bu = np.zeros(len(stimulusTypes)).astype(float)
    cdef np.ndarray[np.float64_t, ndim=1] td = np.zeros(len(stimulusTypes)).astype(float)

    cdef int stimuliCount = 0
    stimulusMap = {}
    for stype in stimulusTypes:
        bu[stimuliCount] = stype["bu"]
        td[stimuliCount] = stype["td"]
        stimulusMap[stype["stimName"]] = stimuliCount
        stimuliCount +=1

    i = 0
    for object in visualObjects:
        x[i] = object["X"]
        y[i] = object["Y"]
        Stype[i] = stimulusMap[object["stimulus"]] 
        onset[i] = object["latency"] + t1onset
        period[i] = object["latency"] + object["duration"] + t1onset
        i+=1

    # Setup Maps
    cdef np.ndarray[np.double_t, ndim=4] EV = np.zeros((stimuliCount + 1, steps, xDim, yDim)) # +1 for Master
    cdef np.ndarray[np.double_t, ndim=4] LV = np.zeros((stimuliCount, steps, xDim, yDim))
    cdef np.ndarray[np.double_t, ndim=4] II = np.zeros((stimuliCount, steps, xDim, yDim))
    
    cdef np.ndarray[np.double_t, ndim=3] AM = np.zeros((steps, xDim, yDim)) + 5 
    cdef np.ndarray[np.double_t, ndim=3] IG = np.zeros((steps, xDim, yDim))

    # Setup Currents
    cdef int currents = 3

    cdef np.ndarray[np.double_t, ndim=4] EV_Current = np.zeros((stimuliCount + 1, currents, xDim, yDim)) # +1 for Master
    cdef np.ndarray[np.double_t, ndim=4] LV_Current = np.zeros((stimuliCount, currents, xDim, yDim))
    cdef np.ndarray[np.double_t, ndim=4] II_Current = np.zeros((stimuliCount, currents, xDim, yDim))

    cdef np.ndarray[np.double_t, ndim=3] AM_Current = np.zeros((currents + 1, xDim, yDim)) # +1 for excite EEG
    AM_Current[0,:,:] += AMexcitebias 
    cdef np.ndarray[np.double_t, ndim=3] IG_Current = np.zeros((currents + 1, xDim, yDim)) # excite_LV, excite_AM

    cdef np.ndarray[np.double_t, ndim=2] trimmedAM = np.zeros((xDim, yDim))
    cdef np.ndarray[np.double_t, ndim=1] N2pc = np.zeros(steps)
    
    for step in range(0, steps):
        for stim in range(0, stimuliCount):
            EV_Current[stim, excite] *= 0
            LV_Current[stim, excite] *= 0
            II_Current[stim, excite] *= 0

            EV_Current[stim, inhib] *= 0
            LV_Current[stim, inhib] *= 0
            II_Current[stim, inhib] *= 0

        EV_Current[stimuliCount, excite] *= 0
        EV_Current[stimuliCount, inhib] *= 0
        
        AM_Current[excite] *= 0
        AM_Current[excite] += AMexcitebias 

        IG_Current[excite_LV] *= 0
        IG_Current[excite_AM] *= 0

        AM_Current[inhib] *= 0
        IG_Current[inhib] *= 0

        if(step == 0):
            prev = 0
        else:
            prev = step-1
        
        for obj in range(0, visObjsCount):
            if(step>=onset[obj] and step < period[obj]):
                EV_Current[Stype[obj], excite, x[obj]-1, y[obj]-1] = EVsalInput # Ev current indices reflect the stype of the object, but when we're in LV we go thru the stims
            
            EV_Current[stimuliCount, excite, x[obj]-1, y[obj]-1] = EVsalInput 

        # feed forward activLVy from EV to LV and AM
        # step through each neuron in these layers
        for xi in range(1, xDim+1):
            for yi in range (1, yDim+1):  
                for stim in range(0, stimuliCount):
                    if(LV[stim, prev, xi-1, yi-1] > LVthresh):
                        II_Current[stim, excite, xi-1, yi-1] += (LV[stim, prev, xi-1,yi-1]-LVthresh) * LVtoII
                    
                    if(II[stim, prev, xi-1, yi-1] > ThreshLV_II):
                        LV_Current[stim, inhib, xi-1, yi-1] +=  (II[stim, prev, xi-1,yi-1]-ThreshLV_II) * ILVoLV
                
                if(AM[prev, xi-1, yi-1] > (Thresh+AM_highthresh) ):
                    IG_Current[inhib, xi-1, yi-1] = (AM[prev, xi-1, yi-1]-Thresh+AM_highthresh) * AMtoIG_inhib # when AM neurons are over thresh they inhib the inhibLVion from IG
                
                # finding boundaries for receptive field
                xmin = max(xi - NNMask ,1) 
                xmax = min(xi + NNMask ,xDim)
                ymin = max(yi - NNMask ,1)
                ymax = min(yi + NNMask ,yDim)

                # gather input from all the neurons within their receptive field
                for x2 in range(xmin, xmax+1): # for a given spot in this neuron's receptive field
                    for y2 in range(ymin, ymax+1):
                        xdiff = x2 - xi + xDim + 1 # xDim+1 is the center of the sombrero
                        ydiff = y2 - yi + yDim + 1

                        RF_local = Gaus_RF[xdiff-1,ydiff-1] # this translates the coordinates from "physical" space to spot on a gaussian
                        
                        attention = 1
                        if AM[prev, x2-1, y2-1]> Thresh:
                            attention = max(1, np.log(AM[prev, x2-1, y2-1] - Thresh + 1) * attentionweight) # this is the equation for when a neuron in AM is above threshold
                        
                        # this is the feedforward to the LV maps
                        for stim in range(0, stimuliCount):
                            if(EV[stim, prev, x2-1,y2-1] >  EVthresh): 
                                # if this neuron is excited in EV...
                                LV_Current[stim, excite, xi-1, yi-1] += (EV[stim, prev, x2-1, y2-1]-EVthresh) * bu[stim] * attention * RF_local #the LV neuron get a cumulation of excitement

                            #LVs feed into ONE attention map
                            if(LV[stim, prev, x2-1, y2-1] > LVthresh):
                                AM_Current[excite, xi-1, yi-1] += (LV[stim, prev, x2-1, y2-1]-LVthresh) * td[stim] *RF_local
                                IG_Current[excite_LV, xi-1, yi-1] += (LV[stim, prev, x2-1, y2-1]-LVthresh) * td[stim] * RF_local
                
                # Attention map inhibLVion: Compute whether any nodes in the attention map have crossed threshold and apply inhibLVion
                AM_Current[inhib, xi-1,yi-1] += max(0, (IG[prev, xi-1,yi-1] - ThreshIG)*LAI )

                if AM[prev, xi-1, yi-1]> Thresh:
                    for x2i in range(1, xDim+1):
                        for y2i in range(1, yDim+1):
                            if x2i !=xi or y2i !=yi:
                                xdiff = x2i - xi + xDim +1 # xDim+1 is the center of the sombrero
                                ydiff = y2i - yi + yDim +1
                                
                                sombrero_local = sombrero[xdiff-1,ydiff-1] # this translates the coordinates from "physical" space to spot on the sombrero
                                if sombrero_local < 0:
                                    IG_Current[excite_AM, x2i-1, y2i-1] += max(0, (AM[prev, xi-1,yi-1]-Thresh) ) * AMtoIG_excite * sombrero_local*(-1.) 

        IG_Current[excite_LV] = np.minimum(IG_Current[excite_LV], MaxLVtoIG)
        IG_Current[excite_AM] = np.minimum(IG_Current[excite_AM], MaxAMtoIG)
        IGexcite = IG_Current[excite_LV] + IG_Current[excite_AM]

        # compute the activation values of all the nodes
        for stim in range(0, stimuliCount):
            #Excite
            EV_Current[stim, excite] = dt_vm* np.multiply( (EE - EV[stim, prev,:,:]) , EV_Current[stim, excite])
            LV_Current[stim, excite] = dt_vm* np.multiply( (EE - LV[stim, prev,:,:]) , LV_Current[stim, excite])
            II_Current[stim, excite] = dt_vm_II* np.multiply( (EE - II[stim, prev,:,:]) , II_Current[stim, excite])

            #Leaks
            EV_Current[stim, leak] = dt_vm* (EL- EV[stim, prev,:,:])
            LV_Current[stim, leak] = dt_vm* (EL- LV[stim, prev,:,:])
            II_Current[stim, leak] = dt_vm_II* (EL- II[stim, prev,:,:])

            #Inhibs
            EV_Current[stim, inhib] = dt_vm * np.multiply((EI-EV[stim, prev,:,:]) , EV_Current[stim, inhib])
            LV_Current[stim, inhib] = dt_vm * np.multiply((EI-LV[stim, prev,:,:]) , LV_Current[stim, inhib])

            #Update activation map
            EV[stim, step,:,:] = np.maximum(EI, EV[stim, prev, :, :] + EV_Current[stim, excite] + EV_Current[stim, inhib] + EV_Current[stim, leak])
            LV[stim, step,:,:] = np.maximum(EI, LV[stim, prev, :, :] + LV_Current[stim, excite] + LV_Current[stim, inhib] + LV_Current[stim, leak])
            II[stim, step,:,:] = np.maximum(EI, II[stim, prev, :, :] + II_Current[stim, excite] + II_Current[stim, leak])  #no inhibLVion on LV_II neurons?


        EV_Current[stimuliCount, excite] = dt_vm* np.multiply((EE-EV[stimuliCount, prev, :, :]) , EV_Current[stimuliCount, excite])
        EV_Current[stimuliCount, leak]   = dt_vm* (EL- EV[stimuliCount, prev, :, :])
        EV_Current[stimuliCount, inhib]  = dt_vm* np.multiply((EI-EV[stimuliCount, prev, :, :]) , EV_Current[stimuliCount, inhib])
        EV[stimuliCount, step, :, :] = np.maximum(EI, EV[stimuliCount, prev, :, :] + EV_Current[stimuliCount, excite] +  EV_Current[stimuliCount, inhib] + EV_Current[stimuliCount, leak])

        AM_Current[excite]    = dt_vm * np.multiply((EE-AM[prev, :, :]) , AM_Current[excite])
        AM_Current[exciteEEG] = dt_vm * np.multiply((EE_EEG-AM[prev, :, :]) , AM_Current[excite])
        IGexcite =      dt_vm_IG* np.multiply((EE-IG[prev, :, :]) ,  IGexcite)
        
        AM_Current[leak] = dt_vm* (EL- AM[prev, :, :])
        IG_Current[leak] = dt_vm_IG* (EL- IG[prev, :, :])

        AM_Current[inhib] = dt_vm * np.multiply((EI-AM[prev, :, :]) , AM_Current[inhib])
        IG_Current[inhib] = dt_vm_IG * np.multiply((EI-IG[prev, :, :]) , IG_Current[inhib]) # there's no IOinhib because those aren't ever inhibited

        AM[step, :, :] = np.maximum(EI, AM[prev, :, :] + AM_Current[excite] + AM_Current[inhib] + AM_Current[leak] ) #+ (rnd.random())*AMnoise)
        IG[step, :, :] = np.maximum(EI, IG[prev, :, :] + IGexcite + IG_Current[inhib] + IG_Current[leak] )

        #making the N2pc where inhibLVion cancels out excLVation
        TrimmedAM = np.maximum(0, AM_Current[exciteEEG] + AM_Current[inhib] )
        N2pc[step] = np.sum(TrimmedAM[0:int(math.ceil(xDim/2.)),:])
        N2pc[step] = N2pc[step] -np.sum(TrimmedAM[int(math.ceil(xDim/2.))+1:,:])


    ## Transposing axes for EV, AM, LV, IG, and II
    EVTransposed = np.transpose(EV, axes=(0, 1, 3, 2))
    AMTransposed = np.transpose(AM, axes=(0, 2, 1))
    LVTransposed = np.transpose(LV, axes=(0, 1, 3, 2))
    IGTransposed = np.transpose(IG, axes=(0, 2, 1))
    IITransposed = np.transpose(II, axes=(0, 1, 3, 2))

    
    return EVTransposed, LVTransposed, IGTransposed, AMTransposed, IITransposed, N2pc, stimulusMap
