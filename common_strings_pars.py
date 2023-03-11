from utils import *

class CombineStrings:
    def __init__(self, date_string = ""):
        self.date_string = '_'+date_string
        self.Additional = ""
        self.COMBINE_ASYMP_LIMIT = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_IMPACT = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_FITDIAGNOSTIC = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_LHS = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"

    def set_date(self, date_string):
        self.date_string = '_'+date_string
        self.COMBINE_ASYMP_LIMIT = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_IMPACT = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_FITDIAGNOSTIC = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_LHS = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"

    def set_tag(self, Additional ):
        self.Additional = Additional
        self.COMBINE_ASYMP_LIMIT = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_IMPACT = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_FITDIAGNOSTIC = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"
        self.COMBINE_LHS = "mH{mH}_{year}"+self.date_string+(self.Additional).upper()+"_{blind}_{Category}"

    def printAll(self):
        logger.debug("{:21}: {}".format("COMBINE_ASYMP_LIMIT",self.COMBINE_ASYMP_LIMIT))
        logger.debug("{:21}: {}".format("COMBINE_IMPACT",self.COMBINE_IMPACT))
        logger.debug("{:21}: {}".format("COMBINE_FITDIAGNOSTIC",self.COMBINE_FITDIAGNOSTIC))
        logger.debug("{:21}: {}".format("COMBINE_LHS",self.COMBINE_LHS))
