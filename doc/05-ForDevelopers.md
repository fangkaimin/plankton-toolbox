# Plankton Toolbox: For developers #

## Introduction ##

This part of the documentation is for software developers who want to develop their own customized 
version of Plankton Toolbox, or to join the development of the standard version of Plankton Toolbox. 
It can also contain useful information for advanced users who want to run the latest development version 
of Plankton Toolbox directly from the Python code.

  * Plankton Toolbox is developed in Python 2.7 and PyQt4.
  * All code is open source and published under the MIT license.
  * The code repository, and other useful information, can be found here: http://plankton-toolbox.org

## Running and developing the Python code ##

If you want to run the latest development version directly from code you have to do this (more detailed
descriptions for each platform is available below):

  * Install Python 2.7
  * Install Python libraries: Pyqt4, Matplotlib, Numpy and Openpyxl.
  * Get a copy of the code from GitHub: [http://plankton-toolbox.org] (http://plankton-toolbox.org)
  * Go to the directory: **cd plankton_toolbox**
  * Start Plankton Toolbox: **python plankton_toolbox_start.py**

## Single file executables ##
PyInstaller is used to create single files executables of the Plankton Toolbox. 
To create an executable file for a specific platform it must be possible to run it directly from Python on that platform. 
It should work on Windows, MacOS and Ubuntu (and probably other with support for Qt/PyQt).
PyInstaller works in the same way on all these platforms.

PyInstaller should not be install, just downloaded and decompressed (unzipped). 
Then you have to open some command/terminal-window and navigate to the directory where the file pyinstaller.py is located. 
Run PyInstaller with some parameters and the produced executable file will then show up in a directory called **<pyinstaller-dir>/plankton_toolbox_start/dist**.

## Develop Plankton Toolbox on Windows ##
_Note: This part needs to be checked and missing steps should be added._

An easy way to set up the needed environment on Windows is to use Python(x,y). 
It includes both PyQt and Matplotlib, and a lot of other useful stuff.

  * Install Python(x,y).
  * Install openpyxl from PyPI. https://pypi.python.org/pypi
  * Download the code from GitHub: [http://plankton-toolbox.org] (http://plankton-toolbox.org)

Test Plankton Toolbox before running pyinstaller:
  * cd <path-to-workspace-directory>/p_plankton_toolbox/src
  * python plankton_toolbox_start.py

### Create executable ###

  * Download PyInstaller and decompress/unzip it into **<path-to-some-directory>>\pyinstaller**
  * **cd <path-to-some-directory>\pyinstaller**
  * **python2.7 pyinstaller.py -F -w <path-to-development-directory>\plankton_toolbox_start.py**

  * Get the executable from **<path-to-some-directory>\pyinstaller\plankton_toolbox_start/dist**

## Develop Plankton Toolbox on MacOS: ##
_Note: This part needs to be checked and missing steps should be added._

  * Install Xcode.
  * Install **Command Line Tools** via the Xcode menu **preferences/downloads**.
  * Install MacPorts from http://www.macports.org
  * **sudo port install cctools **  // This is not always needed, depends on Xcode and MacPorts versions.
  * **sudo port install py27-matplotlib**
  * **sudo port install py27-openpyxl**
  * **sudo port install py27-pyqt4**
  * **cd <path-to-workspace-directory>/p_plankton_toolbox**
  * Get the code from GitHub: [http://plankton-toolbox.org] (http://plankton-toolbox.org)

Test Plankton Toolbox before running pyinstaller:
  * **cd <path-to-workspace-directory>/p_plankton_toolbox/src**
  * **python2.7 plankton_toolbox_start.py**

### Create executable ###

  * Download PyInstaller and decompress it into **<path-to-some-directory>>/pyinstaller**
  * **cd <path-to-some-directory>/pyinstaller**
  * **python2.7 pyinstaller.py -F -w <path-to-development-directory>/plankton_toolbox_start.py**

  * Get the executable from **<path-to-some-directory>/pyinstaller/plankton_toolbox_start/dist**

## Develop Plankton Toolbox on Ubuntu ##
_Note: This part needs to be checked and missing steps should be added._

  * Make sure Python 2.7 and PyQt4 are installed.
  * **sudo apt-get install python-setuptools**
  * **sudo apt-get install python-numpy**
  * **sudo apt-get install python-matplotlib**
  * **sudo easy_install openpyxl**
  * **sudo apt-get install subversion**
  * **cd <path-to-workspace-directory>/p_plankton_toolbox**
  * Get the code from GitHub: [http://plankton-toolbox.org] (http://plankton-toolbox.org)

Test Plankton Toolbox before running pyinstaller:
  * **cd <path-to-workspace-directory>/p_plankton_toolbox/src**
  * **python plankton_toolbox_start.py**

### Create executable ###

  * Download PyInstaller and decompress it into **<path-to-some-directory>>/pyinstaller**
  * **cd <path-to-some-directory>/pyinstaller**
  * **python pyinstaller.py -F -w <path-to-development-directory>/plankton_toolbox_start.py**

  * Get the executable from **<path-to-some-directory>/pyinstaller/plankton_toolbox_start/dist**
  