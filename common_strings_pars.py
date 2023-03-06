import datetime

today = datetime.datetime.now()
date_string = today.strftime("%d%b").lower()
Additional = ""

# NEW
COMBINE_ASYMP_LIMIT = "mH{mH}_{year}_"+date_string+Additional+"_{blind}_{Category}_AsympLimit"
COMBINE_IMPACT = "mH{mH}_{year}_"+date_string+Additional+"_{blind}_{Category}"
COMBINE_FITDIAGNOSTIC = "mH{mH}_{year}_"+date_string+Additional+"_{blind}_{Category}"
COMBINE_LHS = "mH{mH}_{year}_"+date_string+Additional+"_{blind}_{Category}"

# # OLD # Delete below patch once I have all new files
# COMBINE_ASYMP_LIMIT = "mH{mH}_{year}_AsympLimit{blind}_{Category}"
# COMBINE_IMPACT = "mH{mH}_{year}_"+date_string+Additional+"_{blind}_{Category}"
# COMBINE_FITDIAGNOSTIC = "mH{mH}_{year}_"+date_string+Additional+"_{blind}_{Category}"
# COMBINE_LHS = "mH{mH}_{year}_"+date_string+Additional+"_{blind}_{Category}"
