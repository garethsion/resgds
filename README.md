# resgds

Installation 
=============

* Ensure you have github installed on your computer 
* Open the git Bash terminal 
* cd to a working directory 
* Download by executing git clone https://github.com/garethsion/resgds.git
* Once cloned, cd into resgds directory, and run the command 

` python setup.py install '

If installing on Windows 
------------------------
For some annoying reason, gdspy does not easily install by pip on windows, and needs to be installed manually. resgds cannot be installed without gdspy. As of 14/11/2024, I have found the following procedure to work for installing gdspy.

1. Download backports.tarfile by - pip install backports.tarfile
2. git clone the source code of the gdspy library onto your local machine - git clone https://github.com/heitzmann/gdspy.git
3. Download C++>= V14 tools from https://visualstudio.microsoft.com/visual-cpp-build-tools/
4. cd to the gdspy directory you downloaded, and run python setup.py install
5. To check if it worked, cd out of the directory, and run python in the command line. Then try and import gdspy. Don't do this in the gdspy folder, since it won't work here, and will complain of a circular dependence
6. If this has worked, you can now proceed to install resgds
 
