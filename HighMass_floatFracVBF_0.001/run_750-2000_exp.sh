
for type in 1D 2D

  do

  echo ${type}
  for ((n=0; n<13;n++))

    do

      mH=$((750+50*${n}))

      echo ${mH}
      cd ../cards_sm13_${type}_12p9fb_fracVBF_0.001_floatFracVBF/HCG/${mH}/
      echo 'exp'
      combine -n mH${mH}_exp -m ${mH} -M Asymptotic hzz2l2q_13TeV_xs.txt --rMax 1 --run blind > ${type}_mH${mH}_exp.log

      cd -

    done

  for ((n=0; n<13;n++))

    do

      mH=$((1400+50*${n}))

      echo ${mH}
      cd ../cards_sm13_${type}_12p9fb_fracVBF_0.001_floatFracVBF/HCG/${mH}/
      echo 'exp'
      combine -n mH${mH}_exp -m ${mH} -M Asymptotic hzz2l2q_13TeV_xs.txt --rMax 0.035 --run blind > ${type}_mH${mH}_exp.log

      cd -

    done


  done 

