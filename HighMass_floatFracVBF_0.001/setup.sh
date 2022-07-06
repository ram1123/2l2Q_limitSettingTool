


for type in 1D 2D

   do

   echo ${type}

   for ((n=0; n<30;n++))

    do

      mH=$((550+50*${n})) 
      echo ${mH}

      cd ../cards_sm13_${type}_12p9fb_fracVBF_0.001_floatFracVBF/HCG/${mH}/
      sh ../../../prepare.sh

      cd -

    done #type

  done #mH

