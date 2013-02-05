from setuptools import setup

import pandoc
pandoc.core.PANDOC_PATH = '/usr/bin/pandoc'

doc = pandoc.Document()
doc.markdown = open('README.md').read()

description = \
    """
    This module can be used to validate BagitProfiles.
    """

setup(
      name = 'bagit_profile',
      version = '0.0.1',
      url = 'https://github.com/ruebot/bagit-profiles',
      install_requires=['bagit', 'requests'],
      author = 'Mark Jordon, Nick Ruest',
      author_email = 'mjordan@sfu.ca, ruestn@gmail.com',
      py_modules = ['bagit_profile'],
      scripts = ['bagit_profile.py'],
      description = description,
      long_description = doc.rst,
      platforms = ['POSIX'],
      test_suite = 'test',
      classifiers = [
        'License :: Public Domain',
        'Intended Audience :: Developers',
        'Topic :: Communications :: File Sharing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
      ],
)
