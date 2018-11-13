#!/usr/bin/env python

"""
A simple Python module for validating BagIt profiles. See https://github.com/ruebot/bagit-profiles
for more information.

This module is intended for use with https://github.com/edsu/bagit but does not extend it.

Usage:

import bagit
import bagit_profile

# Instantiate an existing Bag using https://github.com/edsu/bagit.
bag = bagit.Bag('mydir')

# Instantiate a profile, supplying its URI.
my_profile = bagit_profile.Profile('http://example.com/bagitprofile.json')

# Validate 'Serialization' and 'Accept-Serialization'. This must be done
# before .validate(bag) is called. 'mydir' is the path to the Bag.
if my_profile.validate_serialization('mydir'):
    print "Serialization validates"
else:
    print "Serialization does not validate"

# Validate the rest of the profile.
if my_profile.validate(bag):
    print "Validates"
else:
    print "Does not validate"

"""

from os.path import join, exists, isdir, isfile, split
import sys
import mimetypes
import logging
import json
if sys.version_info > (3,):
    from urllib.request import urlopen # pylint: no-name-in-module
else:
    from urllib import urlopen # pylint: disable=no-name-in-module

# Define an exceptin class for use within this module.
class ProfileValidationError(Exception):
    # TODO: or just 'pass' instead of __init__ and __str__
    def __init__(self, value):
        super(ProfileValidationError, self).__init__(value)
        self.value = value
    def __str__(self):
        return repr(self.value)


# Define the Profile class.
class Profile(object): # pylint: disable=useless-object-inheritance

    def __init__(self, url, profile=None):
        self.url = url
        if profile is None:
            profile = self.get_profile()
        else:
            if isinstance(profile, dict):
                profile = profile
            else:
                profile = json.loads(profile)
        self.validate_bagit_profile_info(profile)
        self.profile = profile

    def _fail(self, msg):
        logging.error(msg)
        raise ProfileValidationError(msg)

    def _warn(self, msg):
        logging.error(msg)

    def get_profile(self):
        try:
            f = urlopen(self.url)
            profile = f.read()
            if sys.version_info > (3,):
                profile = profile.decode('utf-8')
            profile = json.loads(profile)
        except Exception as e: # pylint: disable=broad-except
            print("Cannot retrieve profile from %s: %s", self.url, e)
            logging.error("Cannot retrieve profile from %s: %s", self.url, e)
            # This is a fatal error.
            sys.exit(1)

        return profile

    # Call all the validate functions other than validate_bagit_profile_info(),
    # which we've already called. 'Serialization' and 'Accept-Serialization'
    #  are validated in validate_serialization().
    def validate(self, bag):
        valid = True
        try:
            self.validate_bag_info(bag)
        except ProfileValidationError as e:
            self._warn("Error in bag-info.txt: %s" % e.value)
            valid = False
        try:
            self.validate_manifests_required(bag)
        except ProfileValidationError as e:
            self._warn("Required manifests not found: %s" % e.value)
            valid = False
        try:
            self.validate_tag_manifests_required(bag)
        except ProfileValidationError as e:
            self._warn("Required tag manifests not found: %s" % e.value)
            valid = False
        try:
            self.validate_tag_files_required(bag)
        except ProfileValidationError as e:
            self._warn("Required tag files not found: %s" % e.value)
            valid = False
        try:
            self.validate_allow_fetch(bag)
        except ProfileValidationError as e:
            self._warn("fetch.txt is present but is not allowed: %s" % e.value)
            valid = False
        try:
            self.validate_accept_bagit_version(bag)
        except ProfileValidationError as e:
            self._warn("Required BagIt version not found: %s" % e.value)
            valid = False
        return valid

    # Check self.profile['bag-profile-info'] to see if "Source-Organization",
    # "External-Description", "Version" and "BagIt-Profile-Identifier" are present.
    def validate_bagit_profile_info(self, profile):
        if 'Source-Organization' not in profile['BagIt-Profile-Info']:
            self._fail("%s: Required 'Source-Organization' tag is not in 'BagIt-Profile-Info'." % profile)
        if 'Version' not in profile['BagIt-Profile-Info']:
            self._warn("%s: Required 'Version' tag is not in 'BagIt-Profile-Info'." % profile)
            return False
        if 'BagIt-Profile-Identifier' not in profile['BagIt-Profile-Info']:
            self._fail("%s: Required 'BagIt-Profile-Identifier' tag is not in 'BagIt-Profile-Info'." % profile)
        return True

    # Validate tags in self.profile['Bag-Info'].
    def validate_bag_info(self, bag):
        # First, check to see if bag-info.txt exists.
        path_to_baginfotxt = join(bag.path, 'bag-info.txt')
        if not exists(path_to_baginfotxt):
            self._fail("%s: bag-info.txt is not present." % bag)
        # Then check for the required 'BagIt-Profile-Identifier' tag and ensure it has the same value
        # as self.url.
        if 'BagIt-Profile-Identifier' not in bag.info:
            self._fail("%s: Required 'BagIt-Profile-Identifier' tag is not in bag-info.txt." % bag)
        else:
            if bag.info['BagIt-Profile-Identifier'] != self.url:
                self._fail("%s: 'BagIt-Profile-Identifier' tag does not contain this profile's URI: <%s> != <%s>" % (
                    bag, bag.info['BagIt-Profile-Identifier'], self.url))
        # Then, iterate through self.profile['Bag-Info'] and if a key has a dict containing a 'required' key that is
        # True, check to see if that key exists in bag.info.
        for tag in self.profile['Bag-Info']:
            config = self.profile['Bag-Info'][tag]
            if 'required' in config and config['required'] is True:
                if tag not in bag.info:
                    self._fail("%s: Required tag '%s' is not present in bag-info.txt." % (bag, tag))
            # If the tag is in bag-info.txt, check to see if the value is constrained.
            if 'values' in config:
                if bag.info[tag] not in config['values']:
                    self._fail("%s: Required tag '%s' is present in bag-info.txt but does not have an allowed value ('%s')." % (bag, tag, bag.info[tag]))
            # If the tag is nonrepeatable, make sure it only exists once. We do this by checking to see if the value for the key is a list.
            if 'repeatable' in config and config['repeatable'] is False:
                value = bag.info.get(tag)
                if isinstance(value, list):
                    self._fail("%s: Nonrepeatable tag '%s' occurs %s times in bag-info.txt." % (bag, tag, len(value)))
        return True

    # For each member of self.profile['manifests_required'], throw an exception if
    # the manifest file is not present.
    def validate_manifests_required(self, bag):
        for manifest_type in self.profile['Manifests-Required']:
            path_to_manifest = join(bag.path, 'manifest-' + manifest_type + '.txt')
            if not exists(path_to_manifest):
                self._fail("%s: Required manifest type '%s' is not present in Bag." %  (bag, manifest_type))
        return True

    # For each member of self.profile['tag_manifests_required'], throw an exception if
    # the tag manifest file is not present.
    def validate_tag_manifests_required(self, bag):
        # Tag manifests are optional, so we return True if none are defined in the profile.
        if 'Tag-Manifests-Required' not in self.profile:
            return True
        for tag_manifest_type in self.profile['Tag-Manifests-Required']:
            path_to_tag_manifest = join(bag.path, 'tagmanifest-' + tag_manifest_type + '.txt')
            if not exists(path_to_tag_manifest):
                self._fail("%s: Required tag manifest type '%s' is not present in Bag." % (bag, tag_manifest_type))
        return True

    # For each member of self.profile['Tag-Files-Required'], throw an exception if
    # the path does not exist.
    def validate_tag_files_required(self, bag):
        # Tag files are optional, so we return True if none are defined in the profile.
        if 'Tag-Files-Required' not in self.profile:
            return True
        for tag_file in self.profile['Tag-Files-Required']:
            path_to_tag_file = join(bag.path, tag_file)
            if not exists(path_to_tag_file):
                self._fail("%s: Required tag file '%s' is not present in Bag." % (bag, path_to_tag_file))
        return True

    # Check to see if this constraint is False, and if it is, then check to see
    # if the fetch.txt file exists. If it does, throw an exception.
    def validate_allow_fetch(self, bag):
        if self.profile['Allow-Fetch.txt'] is False:
            path_to_fetchtxt = join(bag.path, 'fetch.txt')
            if exists(path_to_fetchtxt):
                self._fail("%s: Fetch.txt is present but is not allowed." % bag)
        return True

    # Check the Bag's version, and if it's not in the list of allowed versions,
    # throw an exception.
    def validate_accept_bagit_version(self, bag):
        actual = bag.tags['BagIt-Version']
        allowed = self.profile['Accept-BagIt-Version']
        if actual not in allowed:
            self._fail("%s: Bag version '%s' is not in list of allowed values: %s" % (bag, actual, allowed))
        return True

    # Perform tests on 'Serialization' and 'Accept-Serialization', in one function.
    # Since https://github.com/edsu/bagit can't tell us if a Bag is serialized or
    # not, we need to pass this function the path to the Bag, not the object. Also,
    # this method needs to be called before .validate().
    def validate_serialization(self, path_to_bag):
        # First, perform the two negative tests.
        if not exists(path_to_bag):
            raise IOError("Can't find file %s" % path_to_bag)
        if self.profile['Serialization'] == 'required' and isdir(path_to_bag):
            self._fail("%s: Bag serialization is required but Bag is a directory." % path_to_bag)
        if self.profile['Serialization'] == 'forbidden' and isfile(path_to_bag):
            self._fail("%s: Bag serialization is forbidden but Bag appears is a file." % path_to_bag)

        # Then test to see whether the Bag is serialized (is a file) and whether the mimetype is one
        # of the allowed types.
        if self.profile['Serialization'] == 'required' or self.profile['Serialization'] == 'optional' and isfile(path_to_bag):
            _, bag_file = split(path_to_bag)
            mtype = mimetypes.guess_type(bag_file)
            if mtype[0] not in self.profile['Accept-Serialization']:
                self._fail("%s: Bag serialization is forbidden but Bag appears is a file." % path_to_bag)
        # If we have passed the serialization tests, return True.
        return True


def _main():
    # Command-line version.
    import time
    import bagit
    import optparse # pylint: disable=deprecated-module

    class BagitProfileOptionParser(optparse.OptionParser):
        def __init__(self, *args, **opts):
            optparse.OptionParser.__init__(self, *args, **opts)

    def _make_opt_parser():
        parser = BagitProfileOptionParser(usage='usage: %prog [options] profile_uri bag_dir')
        parser.add_option('--quiet', action='store_true', dest='quiet')
        parser.add_option('--log', action='store', dest='log')
        return parser

    def _configure_logging(opts):
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        if opts.quiet:
            level = logging.ERROR
        else:
            level = logging.INFO
        if opts.log:
            logFile = join(opts.log + '/logs', 'BagitProfile_' + time.strftime('%y_%m_%d') + '.log')
            logging.basicConfig(filename=logFile, level=level, format=log_format)
        if not opts.log:
            logging.basicConfig(filename='BagitProfile' + time.strftime('%y_%m_%d') + '.log', level=level, format=log_format)
        else:
            logging.basicConfig(level=level, format=log_format)

    opt_parser = _make_opt_parser()
    opts, args = opt_parser.parse_args()
    _configure_logging(opts)

    rc = 0

    # Instantiate a profile, supplying its URI.
    profile = Profile(args[0])
    # Instantiate an existing Bag.
    bag = bagit.Bag(args[1])

    # Validate 'Serialization' and 'Accept-Serialization', then perform general validation.
    if profile.validate_serialization(args[1]):
        print("Serialization validates")
    else:
        print("Serialization does not validate")
        rc = 1
        sys.exit(rc)

    # Validate the rest of the profile.
    if profile.validate(bag):
        print("Valdiates")
    else:
        print("Does not validate")

    sys.exit(rc)

if __name__ == '__main__':
    _main()
