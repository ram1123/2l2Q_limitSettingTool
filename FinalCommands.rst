For Expected Upper Limit
==========================

.. bash::

    python makeDCsandWSs.py -y 2018 -s rc -f -1 -setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5 -AdditionalFitOptions " --rAbsAcc 0 --rRelAcc 0.0005 " -c -p

    # The above command worked for run2, run2 ggH, run2 VBF


For FastScan
============

.. bash::

    python makeDCsandWSs.py -y 2018 -s fs -f -1  -howToBlind '-t -1' -setParameterRanges r=-5,5:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10

For Impact Plots
================

.. bash::

    # Check this command
    python makeDCsandWSs.py -y run2 -s ri -f -1 -setParameterRanges r=-1,2:CMS_scale_J_Abs_2018=-10,10:CMS_zz2l2q_sigMELA_merged=-10,10:BTAG_resolved=-10,10:BTAG_merged=-5,5 -AdditionalFitOptions " --rAbsAcc 0 --rRelAcc 0.0005 " -c -p -ss 1
