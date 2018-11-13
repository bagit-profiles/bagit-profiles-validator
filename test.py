import json
import os
import sys
from unittest import TestCase, main

import bagit
from bagit_profile import Profile

PROFILE_URL = 'https://raw.github.com/bagit-profiles/bagit-profiles/master/bagProfileBar.json'

class BagitProfileConstructorTest(TestCase):

    def setUp(self):
        with open('./fixtures/bagProfileBar.json', 'rb') as f:
            self.profile_str = f.read().decode('utf-8') if sys.version_info > (3,) else f.read()
        self.profile_dict = json.loads(self.profile_str)

    def test_profile_kwarg(self):
        profile_url = Profile(PROFILE_URL)
        profile_dict = Profile(PROFILE_URL, profile=self.profile_dict)
        profile_str = Profile(PROFILE_URL, profile=self.profile_str)
        self.assertEqual(json.dumps(profile_url.profile), json.dumps(profile_dict.profile))
        self.assertEqual(json.dumps(profile_str.profile), json.dumps(profile_dict.profile))

class Test_bag_profile(TestCase):

    def setUp(self):
        self.bag = bagit.Bag('fixtures/test-bar')
        self.profile = Profile(PROFILE_URL)
        self.retrieved_profile = self.profile.get_profile()

    def test_validate_bagit_profile_info(self):
        self.assertTrue(self.profile.validate_bagit_profile_info(self.retrieved_profile))

    def test_validate(self):
        self.assertTrue(self.profile.validate(self.bag))

    def test_validate_bag_info(self):
        self.assertTrue(self.profile.validate_bag_info(self.bag))

    def test_validate_manifests_required(self):
        self.assertTrue(self.profile.validate_manifests_required(self.bag))

    def test_validate_allow_fetch(self):
        self.assertTrue(self.profile.validate_allow_fetch(self.bag))

    def test_validate_accept_bagit_version(self):
        self.assertTrue(self.profile.validate_accept_bagit_version(self.bag))

    def test_validate_serialization(self):
        # Test on unzipped Bag.
        self.assertTrue(self.profile.validate_serialization(os.path.abspath("fixtures/test-bar")))
        # Test on zipped Bag.
        self.profile = Profile(PROFILE_URL)
        self.assertTrue(self.profile.validate_serialization(os.path.abspath("fixtures/test-foo.zip")))

if __name__ == '__main__':
    main()
