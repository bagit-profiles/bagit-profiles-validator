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
import os
import sys
#import requests
import mimetypes
import logging
import optparse
import json
import urllib

# Define an exceptin class for use within this module.
class ProfileValidationError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# Define the Profile class.
class Profile(object):
    def __init__(self, url):
        self.url = url
        self.get_profile()

    def get_profile(self):
        try:
            #r = requests.get(self.url)
            #profile = r.json
            f = urllib.urlopen(self.url)
            profile = f.read()
            profile = json.loads(profile)
            self.profile = profile
        except:
            print "Cannot retrieve profile from ", self.url
            logging.error("Cannot retrieve profile from " + self.url)
            # This is a fatal error.
            sys.exit(1) 

        self.validate_bagit_profile_info(profile)
        return self.profile

    # Call all the validate functions other than validate_bagit_profile_info(),
    # which we've already called. 'Serialization' and 'Accept-Serialization'
    #  are validated in validate_serialization().
    def validate(self, bag):
        valid = True
        try:
            self.validate_bag_info(bag)
        except ProfileValidationError as e:
            print "Error in bag-info.txt: ", e.value
            valid = False
        try:
            self.validate_manifests_required(bag)
        except ProfileValidationError as e:
            print "Required manifests not found: ", e.value
            valid = False
        try:
            self.validate_tag_manifests_required(bag)
        except ProfileValidationError as e:
            print "Required tag manifests not found: ", e.value
            valid = False
        try:
            self.validate_tag_files_required(bag)
        except ProfileValidationError as e:
            print "Required tag files not found: ", e.value
            valid = False
        try:
            self.validate_allow_fetch(bag)
        except ProfileValidationError as e:
            print "fetch.txt is present but is not allowed: ", e.value
            valid = False
        try:
            self.validate_accept_bagit_version(bag)
        except ProfileValidationError as e:
            print "Required BagIt version not found: ", e.value
            valid = False
        return valid

    # Check self.profile['bag-profile-info'] to see if "Source-Organization", 
    # "External-Description", "Version" and "BagIt-Profile-Identifier" are present. 
    def validate_bagit_profile_info(self, profile):
        if 'Source-Organization' not in profile['BagIt-Profile-Info']:
            raise ProfileValidationError("Required 'Source-Organization' tag is not in 'BagIt-Profile-Info'.")
            logging.error(profile + "Required 'Source-Organization' tag is not in 'BagIt-Profile-Info'." + '\n')
            return False
        if 'Version' not in profile['BagIt-Profile-Info']:
            # raise ProfileValidationError("Required 'Version' tag is not in 'BagIt-Profile-Info'.")
            logging.error(profile + "Required 'Version' tag is not in 'BagIt-Profile-Info'." + '\n')
            return False
        if 'BagIt-Profile-Identifier' not in profile['BagIt-Profile-Info']:
            raise ProfileValidationError("Required 'BagIt-Profile-Identifier' tag is not in 'BagIt-Profile-Info'.")
            logging.error(profile + "Required 'BagIt-Profile-Identifier' tag is not in 'BagIt-Profile-Info'." + '\n')
            return False
        return True

    # Validate tags in self.profile['Bag-Info']. 
    def validate_bag_info(self, bag):
        # First, check to see if bag-info.txt exists.
        path_to_baginfotxt = os.path.join(bag.path, 'bag-info.txt')
        if not os.path.exists(path_to_baginfotxt):
            raise ProfileValidationError("bag-info.txt is not present.")
            logging.error(bag + "bag-info.txt is not present." + '\n')
            return False
        # Then check for the required 'BagIt-Profile-Identifier' tag and ensure it has the same value
        # as self.url.
        if 'BagIt-Profile-Identifier' not in bag.info:
            raise ProfileValidationError("Required 'BagIt-Profile-Identifier' tag is not in bag-info.txt.")
            logging.error(bag + "Required 'BagIt-Profile-Identifier' tag is not in bag-info.txt." + '\n')
            return False
        else:
            if bag.info['BagIt-Profile-Identifier'] != self.url:
                raise ProfileValidationError("'BagIt-Profile-Identifier' tag does not contain this profile's URI.")
                logging.error(bag + "'BagIt-Profile-Identifier' tag does not contain this profile's URI." + '\n')
        # Then, iterate through self.profile['Bag-Info'] and if a key has a dict containing a 'required' key that is
        # True, check to see if that key exists in bag.info. 
        for tag in self.profile['Bag-Info']:
            config = self.profile['Bag-Info'][tag]
            if 'required' in config and config['required'] is True: 
                if tag not in bag.info:
                    raise ProfileValidationError("Required tag '%s' is not present in bag-info.txt." % (tag))
                    logging.error(bag + "Required tag '%s' is not present in bag-info.txt." % (tag) + '\n')
                # If the tag is in bag-info.txt, check to see if the value is constrained.
                else:
                    if 'values' in config: 
                        if bag.info[tag] not in config['values']:
                            raise ProfileValidationError("Required tag '%s' is present in bag-info.txt but does not have an allowed value ('%s')." % (tag, bag.info[tag]))
                            logging.error(bag + "Required tag '%s' is present in bag-info.txt but does not have an allowed value ('%s')." % (tag, bag.info[tag]) + '\n')

        return True

    # For each member of self.profile['manifests_required'], throw an exception if 
    # the manifest file is not present.
    def validate_manifests_required(self, bag):
        for manifest_type in self.profile['Manifests-Required']:
            path_to_manifest = os.path.join(bag.path, 'manifest-' + manifest_type + '.txt')
            if not os.path.exists(path_to_manifest):
                raise ProfileValidationError("Required manifest type '%s' is not present in Bag." % (manifest_type))
                logging.error(bag + "Required manifest type '%s' is not present in Bag." %  (manifest_type) + '\n')
        return True

    # For each member of self.profile['tag_manifests_required'], throw an exception if 
    # the tag manifest file is not present.
    def validate_tag_manifests_required(self, bag):
        # Tag manifests are optional, so we return True if none are defined in the profile.
        if not self.profile.has_key('Tag-Manifests-Required'):
            return True
        for tag_manifest_type in self.profile['Tag-Manifests-Required']:
            path_to_tag_manifest = os.path.join(bag.path, 'tagmanifest-' + tag_manifest_type + '.txt')
            if not os.path.exists(path_to_tag_manifest):
                raise ProfileValidationError("Required tag manifest type '%s' is not present in Bag." % (tag_manifest_type))
                logging.error(bag + "Required tag manifest type '%s' is not present in Bag." % (tag_manifest_type) + '\n')
        return True

    # For each member of self.profile['Tag-Files-Required'], throw an exception if 
    # the path does not exist.
    def validate_tag_files_required(self, bag):
        # Tag files are optional, so we return True if none are defined in the profile.
        if not self.profile.has_key('Tag-Files-Required'):
            return True
        for tag_file in self.profile['Tag-Files-Required']:
            path_to_tag_file = os.path.join(bag.path, tag_file)
            if not os.path.exists(path_to_tag_file):
                raise ProfileValidationError("Required tag file '%s' is not present in Bag." % (path_to_tag_file))
                logging.error(bag + "Required tag file '%s' is not present in Bag." % (path_to_tag_file) + '\n')
        return True

    # Check to see if this constraint is False, and if it is, then check to see
    # if the fetch.txt file exists. If it does, throw an exception.
    def validate_allow_fetch(self, bag):
        if self.profile['Allow-Fetch.txt'] is False: 
            path_to_fetchtxt = os.path.join(bag.path, 'fetch.txt')
            if os.path.exists(path_to_fetchtxt):
                raise ProfileValidationError("Fetch.txt is present but is not allowed.")
                logging.error(bag + "Fetch.txt is present but is not allowed." + '\n')
        return True

    # Check the Bag's version, and if it's not in the list of allowed versions,
    # throw an exception.
    def validate_accept_bagit_version(self, bag):
        if bag.version not in self.profile['Accept-BagIt-Version']:
            raise ProfileValidationError("Bag version does is not in list of allowed values.")
            logging.error(bag + "Bag version does is not in list of allowed values." + '\n')
        return True

    # Perform tests on 'Serialization' and 'Accept-Serialization', in one function.
    # Since https://github.com/edsu/bagit can't tell us if a Bag is serialized or
    # not, we need to pass this function the path to the Bag, not the object. Also,
    # this method needs to be called before .validate().
    def validate_serialization(self, path_to_bag):
        # First, perform the two negative tests.
        if not os.path.exists(path_to_bag):
            raise IOError("Can't find file %s" % path_to_bag)
        if self.profile['Serialization'] == 'required' and os.path.isdir(path_to_bag):
            raise ProfileValidationError("Bag serialization is required but Bag is a directory.")
            logging.error(path_to_bag + "Bag serialization is required but Bag is a directory." + '\n')
            return False
        if self.profile['Serialization'] == 'forbidden' and os.path.isfile(path_to_bag):
            raise ProfileValidationError("Bag serialization is forbidden but Bag appears is a file.")
            logging.error(path_to_bag + "Bag serialization is forbidden but Bag appears is a file." + '\n')
            return False

        # Then test to see whether the Bag is serialized (is a file) and whether the mimetype is one
        # of the allowed types.
        if self.profile['Serialization'] == 'required' or self.profile['Serialization'] == 'optional' and os.path.isfile(path_to_bag):
            bag_path, bag_file = os.path.split(path_to_bag)
            mtype = mimetypes.guess_type(bag_file)
            if mtype[0] not in self.profile['Accept-Serialization']:
                raise ProfileValidationError("Bag serialization type is not in the list of allowed values.")
                logging.error(path_to_bag + "Bag serialization is forbidden but Bag appears is a file." + '\n')
      
        # If we have passed the serialization tests, return True.
        return True


# Command-line version.
import time
import bagit

class BagitProfileOptionParser(optparse.OptionParser):
  def __init__(self, *args, **opts):
    optparse.OptionParser.__init__(self, *args, **opts)

def _make_opt_parser():
  parser = BagitProfileOptionParser(usage='usage: %prog [options] profile_uri bag_dir')
  parser.add_option('--quiet', action='store_true', dest='quiet')
  parser.add_option('--log', action='store', dest='log')
  return parser

def _configure_logging(opts):
  log_format="%(asctime)s - %(levelname)s - %(message)s"
  if opts.quiet:
    level = logging.ERROR
  else:
    level = logging.INFO
  if opts.log:
    logFile = os.path.join(opts.log + '/logs', 'BagitProfile_' + time.strfime('%y_%m_%d') + '.log')
    logging.basicConfig(filename=logFile, level=level, format=log_format)
  if not opts.log:
    logging.basicConfig(filename='BagitProfile' + time.strftime('%y_%m_%d') + '.log', level=level, format=log_format)
  else:
    logging.basicConfig(level=level, format=log_format)

if __name__ == '__main__':
    opt_parser = _make_opt_parser()
    opts, args = opt_parser.parse_args()
    _configure_logging(opts)
    log = logging.getLogger()

    rc = 0

    # Instantiate a profile, supplying its URI.
    profile = Profile(args[0])
    # Instantiate an existing Bag.
    bag = bagit.Bag(args[1])

    # Validate 'Serialization' and 'Accept-Serialization', then perform general validation.
    if profile.validate_serialization(args[1]):
        print "Serialization validates"
    else:
        print "Serialization does not validate"
        rc = 1
        sys.exit(rc)
        
    # Validate the rest of the profile.
    if profile.validate(bag):
        print "Valdiates"
    else:
        print "Does not validate"

    sys.exit(rc)
