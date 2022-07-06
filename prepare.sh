

   for t in Resolved Merged  

    do
 
      rm hzz2l2q_mumuqq_${t}_13TeV.txt
      rm hzz2l2q_eeqq_${t}_13TeV.txt
      rm hzz2l2q_${t}_13TeV_xs.txt
      rm hzz2l2q_${t}_13TeV_xs.root

      for fs in eeqq_$t mumuqq_$t

      do
        combineCards.py hzz2l2q_${fs}_untagged_13TeV.txt hzz2l2q_${fs}_b-tagged_13TeV.txt hzz2l2q_${fs}_vbf-tagged_13TeV.txt  > hzz2l2q_${fs}_13TeV.txt

      done # fs

      combineCards.py hzz2l2q_mumuqq_${t}_13TeV.txt hzz2l2q_eeqq_${t}_13TeV.txt > hzz2l2q_${t}_13TeV_xs.txt

      for cat in untagged b-tagged vbf-tagged

      do

        combineCards.py hzz2l2q_eeqq_${t}_${cat}_13TeV.txt hzz2l2q_mumuqq_${t}_${cat}_13TeV.txt > hzz2l2q_${t}_${cat}_13TeV.txt        

      done # fs

      #text2workspace.py hzz2l2q_${t}_13TeV_xs.txt -o hzz2l2q_${t}_13TeV_xs.root
  
    done

   combineCards.py hzz2l2q_Resolved_13TeV_xs.txt hzz2l2q_Merged_13TeV_xs.txt > hzz2l2q_13TeV_xs.txt
    
   combineCards.py -s hzz2l2q_Resolved_13TeV_xs.txt hzz2l2q_Merged_13TeV_xs.txt > hzz2l2q_13TeV_xs_NoNuisance.txt

