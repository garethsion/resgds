#!/usr/bin/env python
import gdspy
import os
from subprocess import call
import stat
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
            # kl = call('./klayout_viewer %s' %filename,shell=True)
            file = open("klayout_viewer","w")
            file.write("#!/bin/bash")
            file.write("\n")
            file.write("\n")
            file.write("FOLDER=$PWD")
            file.write("\n")
            file.write("\n")
            file.write("/Applications/klayout.scripts/KLayoutEditor.app/Contents/MacOS/KLayoutEditor.sh -s ${FOLDER}/${@}")
            file.close()

            self.call_bash("klayout_viewer",filename)

    def call_bash(self,filename,gdsfile):
        """
            Method to call created bash scripts with the subprocess module
        """
        st = os.stat(filename)
        os.chmod(filename, st.st_mode | stat.S_IEXEC)
        callname = "./"+ filename
        call([callname, gdsfile]) 
        os.remove(filename)