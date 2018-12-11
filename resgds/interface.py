#!/usr/bin/env python
import gdspy
import os
from subprocess import call
import psutil

class Interface:
    """
    Methods to interface main python scripts with useful bash scripts
    """
    def __init__(self):
        return

    def klayout(self,filename):
        # Check if klayout is already running. If not, write gds and open klayout.
        # If it is, just update the gds file
        if("klayout" in (p.name() for p in psutil.process_iter())):
            #Write the pattern as a gds file
            gdspy.write_gds(filename, unit=1.0e-6, precision=1.0e-9)
        else:
            gdspy.write_gds(filename, unit=1.0e-6, precision=1.0e-9)
            kl = call('./klayout_viewer %s' %filename,shell=True)
