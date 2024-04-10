#! /usr/bin/env python3

import panel as pn
from urllib.request import urlopen

class MonitoringAppDates:
    def __init__(self):
        pn.extension()

    def openFile(self, log):
        open_log = urlopen(log)
        contents_log = open_log.read()
        decoded_line = contents_log.decode("utf-8")
        open_log.close()
        return decoded_line

    def getDates(self):
        sdate = "http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/aweekbefore.txt"
        edate = "http://ftp1.cptec.inpe.br/pesquisa/das/carlos.bastarz/SMNAMonitoringApp/todaym1H.txt"

        start_date = self.openFile(sdate)
        end_date = self.openFile(edate)

        return start_date, end_date
