
cat=$1

for type in 1D 2D

  do

  echo ${type}
  for mH in 700

    do

      echo ${mH}
      cd ../cards_sm13_${type}_12p9fb_fracVBF_0.001_floatFracVBF/HCG/${mH}/
      echo 'exp'
      combine -n mH${mH}_${cat}_exp -m ${mH} -M Asymptotic hzz2l2q_${cat}_13TeV.txt --run blind --rMax 1 
      echo 'obs'
      combine -n mH${mH}_${cat}_obs -m ${mH} -M Asymptotic hzz2l2q_${cat}_13TeV.txt --rMax 1 

      cd -

    done

  done 

