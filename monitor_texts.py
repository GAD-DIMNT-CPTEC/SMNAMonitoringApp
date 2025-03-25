#! /usr/bin/env python3

import panel as pn

class MonitoringAppTexts:
    def __init__(self):
        pn.extension('floatpanel')

    def warnings(self):
        warning_bottom_main = pn.pane.Alert('⚠️ **Warning:** The information shown here does not represent official information and should not be used for decision making.', alert_type='warning')
        return warning_bottom_main
    
    def warnings_anl(self, fname):
        text = (
            "🛑 **Error:** The analysis field is not available for the selected date. File name is **{fname}**."
        )
        message = pn.pane.Alert(text.format(fname=fname), alert_type='danger')
        return message
    
    def warnings_rdiag(self, fname):
        text = (
            "🛑 **Error:** Data unavailable for the selection. File name is **{fname}**."
        )
        message = pn.pane.Alert(text.format(fname=fname), alert_type='danger')
        return message

    def warnings_logs(self, fname):
        text = (
        "🛑 **Error:** The log file is not available for the selected date. File name is **{fname}**."
        )
        message = pn.pane.Alert(text.format(fname=fname), alert_type='danger')
        return message
