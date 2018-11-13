Bagit Profile (validator)
=========================

.. image:: https://img.shields.io/pypi/v/bagit_profile.svg
 :target: https://pypi.org/project/bagit_profile/

.. image:: https://circleci.com/gh/bagit-profiles/bagit-profiles-validator.svg?style=svg
    :target: https://circleci.com/gh/bagit-profiles/bagit-profiles-validator

Description
~~~~~~~~~~~

A simple Python module for validating BagIt profiles. See the `BagIt
Profiles Specification
<https://github.com/bagit-profiles/bagit-profiles/blob/master/README.md>`__
for more information.

This module is intended for use with
`bagit-python <https://github.com/LibraryOfCongress/bagit-python>`__ but does not extend it.

Installation
~~~~~~~~~~~~

``bagit_profile.py`` is a single-file python module that you can drop into
your project as needed or you can install globally with:

1. ``git clone https://github.com/bagit-profiles/bagit-profiles-validator.git``
2. ``cd bagit-profiles-validator``
3. ``sudo python setup.py install``

or:

``pip install bagit_profile``

Usage
~~~~~

.. code:: python

    import bagit
    import bagit_profile

Instantiate an existing Bag using
`bagit <https://github.com/LibraryOfCongress/bagit-python>`__.
``python bag = bagit.Bag('mydir')``

Instantiate a profile, supplying its URI.
``python my_profile = bagit_profile.Profile('http://example.com/bagitprofile.json')``

Validate 'Serialization' and 'Accept-Serialization'. This must be done
before .validate(bag) is called. 'mydir' is the path to the Bag.

.. code:: python

    if my_profile.validate_serialization('mydir'):
        print "Serialization validates"
    else:
        print "Serialization does not validate"

Validate the rest of the profile.

.. code:: python

    if my_profile.validate(bag):
        print "Validates"
    else:
        print "Does not validate"

Or from the commandline:

``bagit_profile.py 'http://uri.for.profile/profile.json' path/to/bag``

Test suite
~~~~~~~~~~

``python setup.py test``

Development
~~~~~~~~~~~

1. `Fork the
   repository <https://help.github.com/articles/fork-a-repo>`__
2. Do something awesome!
3. `Submit a pull
   request <https://help.github.com/articles/creating-a-pull-request>`__
   explianing what your code does

License
~~~~~~~

.. figure:: http://i.creativecommons.org/p/zero/1.0/88x31.png
   :alt: CC0

   CC0
