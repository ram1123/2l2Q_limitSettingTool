
for type in 1D 2D

  do

  echo ${type}
  for mH in 550 600 650

    do

      echo ${mH}
      cd ../cards_sm13_${type}_12p9fb_fracVBF_0.001_floatFracVBF/HCG/${mH}/
      echo 'exp'
      combine -n mH${mH}_exp -m ${mH} -M Asymptotic hzz2l2q_Resolved_13TeV_xs.txt --run blind --rMax 1
      echo 'obs'
      combine -n mH${mH}_obs -m ${mH} -M Asymptotic hzz2l2q_Resolved_13TeV_xs.txt --rMax 1

      cd -

   done

  done 

