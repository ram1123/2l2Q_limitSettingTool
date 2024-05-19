For Expected Upper Limit
==========================


.. code:: bash

    python makeDCsandWSs.py -y 2018 -s rc -f -1 -setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5 -AdditionalFitOptions " --rAbsAcc 0 --rRelAcc 0.0005 " -c -p
    python makeDCsandWSs.py -y allc -s all -f -1 -setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5 -AdditionalFitOptions " --rAbsAcc 0 --rRelAcc 0.0005 " -c -p
    # The above command worked for run2, run2 ggH, run2 VBF

.. code:: bash

    # Floating VBF
    python makeDCsandWSs.py -y all -s plot -f -1 -date "03sep"
    python makeDCsandWSs.py -y run2 -s plot -f -1 -date "03sep"
    python makeDCsandWSs.py -y run2 -s plot -f 0
    python makeDCsandWSs.py -y run2 -s plot -f 1



For FastScan
============

.. code:: bash

    python makeDCsandWSs.py -y 2018 -s fs -f -1  -howToBlind '-t -1' -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10

For Impact Plots
================

.. code:: bash

    python makeDCsandWSs.py -y 2018 -s ri -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 " -signalStrength 1 -ss 1 -c -p
    python makeDCsandWSs.py -y run2 -s ri -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 " -signalStrength 1 -ss 2 -c -p
    python makeDCsandWSs.py -y run2 -s ri -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 " -signalStrength 1 -ss 3 -c -p

    #jialin's record (fixed one sited constrain issue)
    python makeDCsandWSs.py -y 2018 -s ri -ss 1 -c -p -setParameterRanges r=0,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:CMS_zz2lJ_sigma_J_sig=-10,10:CMS_zz2lJ_mean_J_sig=-10,10:CMS_zz2l2q_sigma_j_sig=-10,10:CMS_zz2l2q_mean_m_sig=-10,10:CMS_zz2l2q_mean_e_sig=-10,10:BTAG_resolved=-20,20:frac_VBF=0,1:BTAG_merged=-20,20 -a deepjet -mi 400 -mf 3050 -AdditionalFitOptions "--setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001" --X-rtd FAST_VERTICAL_MORPH -signalStrength 1
    
    # Investigate the command with signal strength = 0
    python makeDCsandWSs.py -y 2018 -s ri -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5   -mi 2000 -mf 2050   -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 " -signalStrength 1 -ss 1

    #  Submitted to condor on 5 September at 8:59 AM
    python makeDCsandWSs.py -y run2 -s riess -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 "  -ss 1 -date '03sep' -c -p
    python makeDCsandWSs.py -y run2 -s riess -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 "  -ss 2 -date '03sep' -c -p
    python makeDCsandWSs.py -y run2 -s riess -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 "  -ss 2 -date '03sep' -c -p

    # Submitted to condor on 5 September at 13:30 AM
    python makeDCsandWSs.py -y run2 -s ri -f -1 -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5  -AdditionalFitOptions " --setRobustFitStrategy 0 --cminFallbackAlgo Minuit,1:10  --cminDefaultMinimizerTolerance 0.001  --setRobustFitTolerance 0.001 "  -ss 1 -date '03sep' -c -p

