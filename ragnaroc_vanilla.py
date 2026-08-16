import numpy as np
import math

def Attnfunction2(xgrid,ygrid,scale1,scale2):
    t = (xgrid**2 + ygrid**2) 
    z1 = -np.exp(-0.5 *t * scale1) 
    z2 =  2*np.exp(-0.5 *t*scale2 )
    #z= z1+ z2
    return z1+z2

def RFfunction(xgrid,ygrid,scale):
    t   = (xgrid**2 + ygrid**2) 
    #z = np.exp(-0.5 *t*scale )
    return np.exp(-0.5 *t*scale )


def Ragnaroc3C_vanilla(locx, locy, Type1BottomUp, Type2BottomUp, Type3BottomUp, Type1TopDown, Type2TopDown, Type3TopDown, latency, duration, Stype,  steps, videoinput,*args):
    la=len(args)
    #xi, yi, xk, yk, step, NNMask, xmin, xmax, ymin, ymax, x2, y2
    xdim = 27
    ydim = 27
    t1onset = 100-1 #making this immediate for testing purposes, change back when doing sims 
    #if steps==0:
    #   steps=900
    
    fdur=0
    if np.shape(videoinput)[2] >1:
       fdur = math.ceil((steps+1)/np.shape(videoinput)[2])
       print('Frame duration= '+str(fdur))

    videoframe = 0
    count=1

    dt_vm = .015
    dt_vm_IG= 0.04
    dt_vm_II = .0025 
    EE_EEG= 65.
    EE = 30. 
    EL= 0.
    EI = -10.
    AMFloorval = 0.
    AMCeilval = 30.
    LV_1Decider = 0
    individuation= .2
    LV_2Decider= 0.
    AMnoise = 0.
    AMexcitebias = .2
    LV_1excitebias = 0.
    stimOnset = latency + t1onset
    EVsalInput = 1.
    LAI = .45 # strength of localized inhibLVion in the AM
    ThreshLV_II = 0. #threshold when LV II neurons begin inhibLVing their buddy LV neurons
    Thresh = 14. # this was 11 %threshold for attentional amplification
    ThreshIG = 8. 
    attentionweight = 2. #magnLVude of attentional amplification
    EVthresh = 7. 
    LVthresh = 5. 
    AM_highthresh = 8 
    EVtoLV_1 = Type1BottomUp 
    EVtoLV_2 = Type2BottomUp
    EVtoLV_3 = Type3BottomUp
    LV_1toAM = Type1TopDown 
    LV_2toAM = Type2TopDown
    LV_3toAM = Type3TopDown

    AMtoIG_inhib =.25 #this is the coefficient for inhibLVion coming from the single buddy AM neuron
    AMtoIG_excite =.4 
    LV_1toIG =Type1TopDown #this is the excLVation of LV neurons to IG neuron
    LV_2toIG =Type2TopDown
    LV_3toIG =Type3TopDown
    LVtoII = .02 #this is the excLVation from LV to II neurons of the same map
    ILVoLV = 6.5 #inhibLVion of II onto LV's buddy LV neuron
    MaxLVtoIG = 0.35 #this is the maximum amount that the LV neurons can excite IG neurons
    MaxAMtoIG = 0.35 #this is the maximum amount that the AM neurons can excite IG neurons
    #cdef double LV_1Decider
    #cdef double LV_2Decider
    
    xx = np.arange(-xdim, xdim+1,1)
    yy = np.arange(-ydim, ydim+1,1)
    xm, ym = np.meshgrid(xx, yy)
    sombrero = Attnfunction2(xm,ym,.07,individuation)
    EV_1 = np.zeros([xdim, ydim])
    EV_2 = np.zeros((xdim,ydim))
    EV_3 = np.zeros((xdim,ydim))
    EV_Master= np.zeros((xdim,ydim))
    LV_1= np.zeros((xdim,ydim)) #was -.5
    LV_2= np.zeros((xdim,ydim))
    LV_3= np.zeros((xdim,ydim))
    LV_II1= np.zeros((xdim,ydim))
    LV_II2 = np.zeros((xdim,ydim))
    LV_II3 = np.zeros((xdim,ydim))

    AM = np.zeros((xdim,ydim))+5 #was +5
    IG= np.zeros((xdim,ydim)) #%takes in excLVation from AM and LV, sends inhibLVion to 1 AM neuron
    lastAMExcite = np.zeros((xdim,ydim)) #very last state of the A
    
    EV_1excite = np.zeros((xdim,ydim))
    EV_2excite = np.zeros((xdim,ydim))
    EV_3excite = np.zeros((xdim,ydim))
    EV_Masterexcite = np.zeros((xdim,ydim))
    LV_1excite = np.zeros((xdim,ydim))+LV_1excitebias
    LV_2excite =np.zeros((xdim,ydim))
    LV_3excite =np.zeros((xdim,ydim))
    LV_II1excite= np.zeros((xdim,ydim))
    LV_II2excite= np.zeros((xdim,ydim))
    LV_II3excite= np.zeros((xdim,ydim))
    AMexcite = np.zeros((xdim,ydim)) + AMexcitebias 
    IGexcite_LV = np.zeros((xdim,ydim))
    IGexcite_AM = np.zeros((xdim,ydim))

    EV_1inhib= np.zeros((xdim,ydim))
    EV_2inhib= np.zeros((xdim,ydim))
    EV_3inhib= np.zeros((xdim,ydim))
    EV_Masterinhib= np.zeros((xdim,ydim))
    LV_1inhib= np.zeros((xdim,ydim))
    LV_2inhib= np.zeros((xdim,ydim))
    LV_3inhib= np.zeros((xdim,ydim))
    AMinhib = np.zeros((xdim,ydim))
    IGinhib = np.zeros((xdim,ydim))
    
    EV_1leak = np.zeros((xdim,ydim)) #added
    EV_2leak = np.zeros((xdim,ydim)) #added
    EV_3leak = np.zeros((xdim,ydim)) #added
    EV_Masterleak = np.zeros((xdim,ydim)) #added
    LV_1leak = np.zeros((xdim,ydim)) #added
    LV_2leak = np.zeros((xdim,ydim)) #added
    LV_3leak = np.zeros((xdim,ydim)) #added
    LV_II1leak= np.zeros((xdim,ydim)) #added
    LV_II2leak= np.zeros((xdim,ydim)) #added
    AMexcite_EEG = np.zeros((xdim,ydim)) #added
    AMleak= np.zeros((xdim,ydim)) #added
    IGleak = np.zeros((xdim,ydim)) #added
    TrimmedAM=np.zeros((xdim,ydim))
    
    EV_1History = np.zeros((xdim,ydim,steps))
    EV_2History = np.zeros((xdim,ydim,steps))
    EV_3History = np.zeros((xdim,ydim,steps))
    EV_MasterHistory  = np.zeros((xdim,ydim,steps))
    LV_1History = np.zeros((xdim,ydim,steps))
    LV_2History = np.zeros((xdim,ydim,steps))
    LV_3History = np.zeros((xdim,ydim,steps))
    LV_II1History = np.zeros((xdim,ydim,steps))
    LV_II2History = np.zeros((xdim,ydim,steps))
    LV_II3History = np.zeros((xdim,ydim,steps))
    LV_1exciteHistory=np.zeros((xdim,ydim,steps))   
    AMHistory = np.zeros((xdim,ydim,steps))
    IGHistory = np.zeros((xdim,ydim,steps))
    AMinhibHistory =np.zeros((xdim,ydim,steps))
    LV_1inhibHistory =np.zeros((xdim,ydim,steps)) #added
    LV_2inhibHistory =np.zeros((xdim,ydim,steps)) #added
    LV_3inhibHistory =np.zeros((xdim,ydim,steps)) #added
    AMexciteHistory = np.zeros((xdim,ydim,steps)) #added
    IGexcite_LVHistory = np.zeros((xdim,ydim,steps)) #added
    IGexcite_AMHistory = np.zeros((xdim,ydim,steps)) #added
    AMexcite_EEGHistory = np.zeros((xdim,ydim,steps))
    TrimmedAMHistory=np.zeros((xdim,ydim,steps))
    N2pc_exciteOnly=np.zeros(steps)#added
    N2pc_exciteInhib0=np.zeros(steps)#added
    N2pc_exciteInhib=np.zeros(steps)#added
    LV_1DeciderHistory = np.zeros(steps)
    LV_2DeciderHistory= np.zeros(steps)
    LV_3DeciderHistory= np.zeros(steps)

    
    
    RFsize = 1 #was 1 this is going to set the center width for the gaussian
    Attention=np.ones(steps)# Par['attention']=np.ones(Par['steps'])
    Gaus_RF0 = RFfunction(xm,ym,RFsize)
    Gaus_RF = Gaus_RF0/(Gaus_RF0.max())
    
    for step in range(0,steps): #Par.t1onset-1 when I need to walk through
    #print(step)
       if step %100==0: #this is to see how slow LV's working
          print(step)
       if fdur>0 and count<fdur:
           count=count+1
       elif  fdur>0 and count>=fdur:  
          videoframe=videoframe+1 
          print('videoframe='+str(videoframe))
          count=1
           
        #start all the excLVation fields at zero at the start of each step
    
       EV_1excite = 0*EV_1excite
       EV_2excite = 0*EV_2excite
       EV_3excite = 0*EV_3excite
       EV_Masterexcite = 0*EV_Masterexcite
       LV_1excite = 0*LV_1excite+LV_1excitebias
       LV_2excite =0*LV_2excite
       LV_3excite =0*LV_3excite
       LV_II1excite= 0*LV_II1excite
       LV_II2excite= 0*LV_II2excite
       LV_II3excite= 0*LV_II3excite
       AMexcite =0* AMexcite+AMexcitebias
       IGexcite_LV =0* IGexcite_LV
       IGexcite_AM =0*IGexcite_AM

       EV_1inhib= 0*EV_1inhib
       EV_2inhib= 0*EV_2inhib
       EV_3inhib= 0*EV_3inhib
       
       EV_Masterinhib= 0*EV_Masterinhib
       LV_1inhib= 0*LV_1inhib
       LV_2inhib= 0*LV_2inhib
       LV_3inhib= 0*LV_3inhib
       AMinhib = 0*AMinhib
       IGinhib = 0*IGinhib
        ###############################################################################    
        #stimulus input to EV
       if np.shape(videoinput)[2] <=1: 
         #print('OK1')
         for ii in range(0,len(locx)):
            #is T1 on screen?
          if ( step >= stimOnset[ii] and step < stimOnset[ii] + duration[ii]):
            if Stype[ii]==1:
               EV_1excite[locx[ii]-1,locy[ii]-1] = EVsalInput
              
            if Stype[ii]==2:
               EV_2excite[locx[ii]-1,locy[ii]-1] = EVsalInput
            if Stype[ii]==3:
               EV_3excite[locx[ii]-1,locy[ii]-1] = EVsalInput
          
          EV_Masterexcite[locx[ii]-1,locy[ii]-1] = EVsalInput

       if videoframe<=np.shape(videoinput)[2]-1 and np.shape(videoinput)[2]>1:
            
            EV_1excite =np.squeeze(videoinput[:,:,videoframe])
           # print('OK3')
       else:
            EV_1excite =np.zeros((xdim,ydim))
        
        ###############################################################################    

        ###############################################################################
        #feed forward activLVy from EV to LV and AM
        #step through each neuron in these layers
       for xi in range(1, xdim+1):
         for yi in range (1, ydim+1):        
           if LV_1[xi-1,yi-1] > LVthresh:
             LV_II1excite[xi-1,yi-1] = LV_II1excite[xi-1,yi-1]+(LV_1[xi-1,yi-1]-LVthresh)*LVtoII
             #if np.sum(LV_II1excite)>0:
             #print('II_excite'+str(LV_II1excite[xi-1,yi-1]))
           if LV_2[xi-1,yi-1] > LVthresh:
              LV_II2excite[xi-1,yi-1] = LV_II2excite[xi-1,yi-1]+(LV_2[xi-1,yi-1]-LVthresh)*LVtoII
           if LV_3[xi-1,yi-1] > LVthresh:
              LV_II3excite[xi-1,yi-1] = LV_II3excite[xi-1,yi-1]+(LV_3[xi-1,yi-1]-LVthresh)*LVtoII
                    
           if AM[xi-1,yi-1] > (Thresh+AM_highthresh):
              IGinhib[xi-1,yi-1] = (AM[xi-1,yi-1]-Thresh+AM_highthresh)*AMtoIG_inhib #when AM neurons are over thresh they inhib the inhibLVion from IG
             #print('IG')
           if LV_II1[xi-1,yi-1] > ThreshLV_II:
              LV_1inhib[xi-1,yi-1] = LV_1inhib[xi-1,yi-1]+(LV_II1[xi-1,yi-1] - ThreshLV_II)*ILVoLV
           if LV_II2[xi-1,yi-1] > ThreshLV_II:
              LV_2inhib[xi-1,yi-1] = LV_2inhib[xi-1,yi-1]+(LV_II2[xi-1,yi-1] - ThreshLV_II)*ILVoLV
           if LV_II3[xi-1,yi-1] > ThreshLV_II:
              LV_3inhib[xi-1,yi-1] = LV_3inhib[xi-1,yi-1]+(LV_II3[xi-1,yi-1] - ThreshLV_II)*ILVoLV
           #print('OK3')
           NNMask=3# 
           xmin = max(xi- NNMask,1) #finding boundaries for receptive field
           xmax = min(xi+ NNMask ,xdim)
           ymin = max(yi- NNMask ,1)
           ymax = min(yi+ NNMask ,ydim)
        
          #gather input from all the neurons wLVhin their receptive field
           for x2 in range(xmin,xmax+1): #for a given spot in this neuron's receptive field
              for y2 in range(ymin,ymax+1):
                  xdiff = x2 - xi + xdim + 1 #Par.xdim+1 is the center of the sombrero
                  ydiff = y2 - yi + ydim + 1

                  RF_local = Gaus_RF[xdiff-1,ydiff-1] #this translates the coordinates from "physical" space to spot on a gaussian
                  
                  attention = 1
                  if AM[x2-1,y2-1]> Thresh:
                     attention = max(1,np.log(AM[x2-1,y2-1] -Thresh +1)*attentionweight) #this is the equation for when a neuron in AM is above threshold
                     
                  #if x2 == 7 and y2 == 14:
                   #  Attention[step] = attention
                                  
                  #this is the feedforward to the type1 LV map
                  if EV_1[x2-1,y2-1] >  EVthresh: #if this neuron is excited in EV...
                      LV_1excite[xi-1,yi-1] =  LV_1excite[xi-1,yi-1] +(EV_1[x2-1,y2-1]-EVthresh)*EVtoLV_1 *attention*RF_local #the LV neuron get a cumulation of excitement
                  #this is the feedforward to the type2 LV map
                  if EV_2[x2-1,y2-1] > EVthresh: #if this neuron is excited in EV...
                      LV_2excite[xi-1,yi-1] =  LV_2excite[xi-1,yi-1] +(EV_2[x2-1,y2-1]-EVthresh)*EVtoLV_2 *attention*RF_local #the LV neuron get a cumulation of excitement
                  #this is the feedforward to the type3 LV map
                  if EV_3[x2-1,y2-1] > EVthresh: #if this neuron is excited in EV...
                      LV_3excite[xi-1,yi-1] =  LV_3excite[xi-1,yi-1] +(EV_3[x2-1,y2-1]-EVthresh)*EVtoLV_3 *attention*RF_local #the LV neuron get a cumulation of excitement
                      
                  #LV1, LV2 and LV3  feed into ONE attention map
                  if LV_1[x2-1,y2-1] > LVthresh:
                      AMexcite[xi-1,yi-1] =    AMexcite[xi-1,yi-1] +    (LV_1[x2-1,y2-1]-LVthresh)*LV_1toAM*RF_local
                      IGexcite_LV[xi-1,yi-1] = IGexcite_LV[xi-1,yi-1] + (LV_1[x2-1,y2-1]-LVthresh)*LV_1toIG*RF_local
                  if LV_2[x2-1,y2-1] > LVthresh:
                      AMexcite[xi-1,yi-1] =    AMexcite[xi-1,yi-1] +    (LV_2[x2-1,y2-1]-LVthresh)*LV_2toAM*RF_local
                      IGexcite_LV[xi-1,yi-1] = IGexcite_LV[xi-1,yi-1] + (LV_2[x2-1,y2-1]-LVthresh)*LV_2toIG*RF_local
                  if LV_3[x2-1,y2-1] > LVthresh:
                      AMexcite[xi-1,yi-1] =    AMexcite[xi-1,yi-1] +    (LV_3[x2-1,y2-1]-LVthresh)*LV_3toAM*RF_local
                      IGexcite_LV[xi-1,yi-1] = IGexcite_LV[xi-1,yi-1] + (LV_3[x2-1,y2-1]-LVthresh)*LV_3toIG*RF_local

            # attention map inhibLVion
            #compute whether any nodes in the attention map have crossed threshold
            #and apply inhibLVion
            ###############################################################################
           AMinhib[xi-1,yi-1] = AMinhib[xi-1,yi-1] + max(0,(IG[xi-1,yi-1] - ThreshIG)*LAI)
           #print('OK4')
           if AM[xi-1,yi-1]> Thresh:
                #print('AM above Threshold='+str(AM[xi-1,yi-1]))
                for x2i in range(1, ydim+1):
                    for y2i in range(1, 27+1):
                        if x2i !=xi or y2i !=yi:
                            xdiff = x2i - xi + xdim +1 #Par.xdim+1 is the center of the sombrero
                            ydiff = y2i - yi + ydim +1
                            
                            sombrero_local = sombrero[xdiff-1,ydiff-1] #this translates the coordinates from "physical" space to spot on the sombrero
                            #print('SL='+str(sombrero_local))
                            if sombrero_local < 0:
                               #print('Sombrero neg')
                               IGexcite_AM[x2i-1,y2i-1] = IGexcite_AM[x2i-1,y2i-1]+max(0,(AM[xi-1,yi-1]-Thresh)) * AMtoIG_excite * sombrero_local*(-1.)    
 
        ################################################################################                            
        ###############################################################################
        #    #print(Par['IGexcite_LV'].min())                    
       IGexcite_LV = np.minimum(IGexcite_LV, MaxLVtoIG)
       IGexcite_AM = np.minimum(MaxAMtoIG, IGexcite_AM)
       IGexcite = IGexcite_LV + IGexcite_AM
        # Par.IGexcite(x,y) = 0;
        ###############################################################################
        ###############################################################################
        # compute the activation values of all the nodes        
       EV_1excite =      dt_vm* np.multiply((EE-EV_1) , EV_1excite)
       EV_2excite =      dt_vm* np.multiply( (EE-EV_2) , EV_2excite)
       EV_3excite =      dt_vm* np.multiply( (EE-EV_3) , EV_3excite)
       EV_Masterexcite = dt_vm* np.multiply((EE-EV_Master) , EV_Masterexcite)
       LV_1excite =      dt_vm* np.multiply((EE-LV_1) , LV_1excite)
       LV_2excite =      dt_vm* np.multiply((EE-LV_2) , LV_2excite)
       LV_3excite =      dt_vm* np.multiply((EE-LV_3) , LV_3excite)
       LV_II1excite =    dt_vm_II* np.multiply((EE-LV_II1) , LV_II1excite)
       LV_II2excite =    dt_vm_II* np.multiply((EE-LV_II2) , LV_II2excite)
       LV_II3excite =    dt_vm_II* np.multiply((EE-LV_II3) , LV_II3excite)

        
       lastAMExcite  = AMexcite
       AMexcite =     dt_vm * np.multiply((EE-AM) , AMexcite)
       AMexcite_EEG = dt_vm * np.multiply((EE_EEG-AM) , AMexcite)
       IGexcite=      dt_vm_IG* np.multiply((EE-IG) ,  IGexcite)
        
        #everyone leaks
       EV_1leak =       dt_vm* (EL- EV_1)
       EV_2leak =       dt_vm* (EL- EV_2)
       EV_3leak =       dt_vm* (EL- EV_3)
       EV_Masterleak =  dt_vm* (EL- EV_Master)
       LV_1leak =       dt_vm* (EL- LV_1)
       LV_2leak =       dt_vm* (EL- LV_2)
       LV_3leak =       dt_vm* (EL- LV_3)
       LV_II1leak =     dt_vm_II* (EL- LV_II1)
       LV_II2leak =     dt_vm_II* (EL- LV_II2)
       LV_II3leak =     dt_vm_II* (EL- LV_II3)
       
       
       AMleak =         dt_vm* (EL- AM)
       IGleak =         dt_vm_IG* (EL- IG)
        
       LV_1inhibHistory[:,:,step] = LV_1inhib
       LV_2inhibHistory[:,:,step] = LV_2inhib
       LV_3inhibHistory[:,:,step] = LV_3inhib
        
        
        #everyone's inhibLVion gets sorted
       EV_1inhib =      dt_vm * np.multiply((EI-EV_1) , EV_1inhib)
       EV_2inhib =      dt_vm * np.multiply((EI-EV_2) , EV_2inhib)
       EV_3inhib =      dt_vm * np.multiply((EI-EV_3) , EV_3inhib)
       EV_Masterinhib = dt_vm * np.multiply((EI-EV_Master) , EV_Masterinhib)
       LV_1inhib =      dt_vm * np.multiply((EI-LV_1) , LV_1inhib)
       LV_2inhib =      dt_vm * np.multiply((EI-LV_2) , LV_2inhib)
       LV_3inhib =      dt_vm * np.multiply((EI-LV_3) , LV_3inhib)
       AMinhib =        dt_vm * np.multiply((EI-AM) , AMinhib)
       IGinhib=         dt_vm_IG * np.multiply((EI-IG) , IGinhib) #there's no IOinhib because those aren't ever inhibited
        
        
       EV_1 =      np.maximum(EI, EV_1 + EV_1excite +  EV_1inhib + EV_1leak)
       EV_2 =      np.maximum(EI, EV_2 + EV_2excite +  EV_2inhib + EV_2leak)
       EV_3 =      np.maximum(EI, EV_3 + EV_3excite +  EV_3inhib + EV_3leak)
       EV_Master = np.maximum(EI, EV_Master + EV_Masterexcite +  EV_Masterinhib + EV_Masterleak)
       LV_1 =      np.maximum(EI, LV_1 + LV_1excite +  LV_1inhib + LV_1leak)
       LV_2 =      np.maximum(EI, LV_2 + LV_2excite +  LV_2inhib + LV_2leak)
       LV_3 =      np.maximum(EI, LV_3 + LV_3excite +  LV_3inhib + LV_3leak)
       LV_II1 =    np.maximum(EI, LV_II1 + LV_II1excite + LV_II1leak)  #no inhibLVion on LV_II neurons?
       LV_II2 =    np.maximum(EI, LV_II2 + LV_II2excite + LV_II2leak)
       LV_II3 =    np.maximum(EI, LV_II3 + LV_II3excite + LV_II3leak)

        
       AM = np.maximum(EI, AM + AMexcite +  AMinhib + AMleak )#+ (rnd.random())*AMnoise)
       IG = np.maximum(EI, IG + IGexcite +  IGinhib + IGleak)

       LV_1data = LV_1.copy()
       LV_1data[np.where(LV_1data<=.5)] = 0
       LV_2data = LV_2.copy()
       LV_2data[np.where(LV_2data<=.5)] = 0
       LV_3data = LV_3.copy()
       LV_3data[np.where(LV_3data<=.5)] = 0
       LV_1Decider = np.sum(LV_1data) #this was 0
       LV_2Decider = np.sum(LV_2data)
       LV_3Decider = np.sum(LV_3data)

        
        # store histories
       EV_1History[:,:,step] =         EV_1
       EV_2History[:,:,step] =         EV_2
       EV_3History[:,:,step] =         EV_3

       EV_MasterHistory[:,:,step] =    EV_Master
       LV_1History[:,:,step] =         LV_1 #this is what we will integrate to calculate accuracy
       LV_2History[:,:,step] =         LV_2
       LV_3History[:,:,step] =         LV_3
       LV_II1History[:,:,step] =       LV_II1
       LV_II2History[:,:,step] =       LV_II2
       LV_II3History[:,:,step] =       LV_II3

       LV_1exciteHistory[:,:,step] =   LV_1excite
       AMinhibHistory[:,:,step] =      AMinhib
       AMexciteHistory[:,:,step] =     AMexcite
       AMexcite_EEGHistory[:,:,step] = AMexcite_EEG
       AMHistory[:,:,step] =           AM
       IGexcite_LVHistory[:,:,step]=   IGexcite_LV
       IGexcite_AMHistory[:,:,step]=   IGexcite_AM 
       IGHistory[:,:,step] =           IG
       LV_1DeciderHistory[step]= LV_1Decider
       LV_2DeciderHistory[step]= LV_2Decider
       LV_3DeciderHistory[step]= LV_3Decider

        #making the N2pc where inhibLVion cancels out excLVation
       TrimmedAM = np.maximum(0,AMexcite_EEG+AMinhib)
       TrimmedAMHistory[:,:,step]= TrimmedAM
       N2pc_exciteInhib0[step] = np.sum(TrimmedAM[0:int(math.ceil(xdim/2.)),:])
       N2pc_exciteInhib0[step] = N2pc_exciteInhib0[step] -np.sum(TrimmedAM[int(math.ceil(xdim/2.))+1:,:])
    
    N2pc=N2pc_exciteInhib0
    return EV_1History,EV_2History,LV_1History, LV_2History,IGHistory,AMHistory,LV_II1History,LV_II2History,N2pc