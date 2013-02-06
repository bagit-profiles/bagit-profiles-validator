Bagit Profile (validator)
=========================

Description
~~~~~~~~~~~

A simple Python module for validating BagIt profiles. See the `BagIt
Profiles Specification
(draft) <https://github.com/ruebot/bagit-profiles/blob/master/README.md>`_
for more information.

This module is intended for use with
`bagit <https://github.com/edsu/bagit>`_ but does not extend it.

Installation
~~~~~~~~~~~~

bagit\_profile.py is a single-file python module that you can drop into
your project as needed or you can install globally with:

1. ``git clone https://github.com/ruebot/bagit-profiles-validator.git``
2. ``cd bagit-profiles/python``
3. ``sudo python setup.py install``

or:

``pip install bagit_profile``

Usage
~~~~~

::

    import bagit
    import bagit_profile

Instantiate an existing Bag using
`bagit <https://github.com/edsu/bagit>`_.
``python bag = bagit.Bag('mydir')``

Instantiate a profile, supplying its URI.
``python my_profile = bagit_profile.Profile('http://example.com/bagitprofile.json')``

Validate 'Serialization' and 'Accept-Serialization'. This must be done
before .validate(bag) is called. 'mydir' is the path to the Bag.

::

    if my_profile.validate_serialization('mydir'):
        print "Serialization validates"
    else:
        print "Serialization does not validate"

Validate the rest of the profile.

::

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

1. `Fork the repository <https://help.github.com/articles/fork-a-repo>`_
2. Do something awesome!
3. `Submit a pull
   request <https://help.github.com/articles/creating-a-pull-request>`_
   explianing what your code does

License
~~~~~~~

.. figure:: http://i.creativecommons.org/p/zero/1.0/88x31.png
   :align: center
   :alt: CC0

   CC0
