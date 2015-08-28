from distutils.core import setup, Extension
import distutils.sysconfig
sysconfig = distutils.sysconfig.get_config_vars()
import os, sys

setup(name="pycheckbook",
      version = "0.52",
      description = "Python checkbook manager",
      author = "vnr vjiet",
      author_email = "msaikalyan@yahoo.com",
      licence = "GPL",
      packages = ["pycheckbook"],
      scripts = ["PyCheckbook.py"]
      )

