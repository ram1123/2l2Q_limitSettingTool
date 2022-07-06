

 cat=$1 

 sh run_550-700_cat.sh $cat > run_550-700_${cat}.log 2>&1 &

 sh run_700_cat.sh $cat > run_700_${cat}.log 2>&1 &

 sh run_750-2000_exp_cat.sh $cat > run_750-2000_exp_${cat}.log 2>&1 &

 sh run_750-2000_obs_cat.sh $cat > run_750-2000_obs_${cat}.log 2>&1 &

