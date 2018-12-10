from setuptools import setup

description = \
    """
    This module can be used to validate BagitProfiles.
    """
setup(
      name = 'bagit_profile',
      version = '1.3.0',
      url = 'https://github.com/bagit-profiles/bagit-profiles-validator',
      install_requires=['bagit', 'requests'],
      author = 'Mark Jordan, Nick Ruest',
      author_email = 'mjordan@sfu.ca, ruestn@gmail.com',
      license = 'CC0',
      py_modules = ['bagit_profile'],
      scripts = ['bagit_profile.py'],
      description = description,
      long_description = open('README.rst').read(),
      package_data = { '': ['README.rst'] },
      platforms = ['POSIX'],
      test_suite = 'test',
      classifiers = [
        'License :: Public Domain',
        'Intended Audience :: Developers',
        'Topic :: Communications :: File Sharing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Filesystems',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
      ],
)
