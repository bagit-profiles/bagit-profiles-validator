import json
import os
import sys
from os.path import isdir, join
from unittest import TestCase, main
from shutil import rmtree, copytree

import bagit
from bagit_profile import Profile, find_tag_files

PROFILE_URL = 'https://raw.github.com/bagit-profiles/bagit-profiles/master/bagProfileBar.json'

# pylint: disable=multiple-statements

class TagFilesAllowedTest(TestCase):

    def tearDown(self):
        if isdir(self.bagdir):
            rmtree(self.bagdir)

    def setUp(self):
        self.bagdir = join('/tmp', 'bagit-profile-test-bagdir')
        if isdir(self.bagdir):
            rmtree(self.bagdir)
        copytree('./fixtures/test-tag-files-allowed/bag', self.bagdir)
        with open(join('./fixtures/test-tag-files-allowed/profile.json'), 'r') as f:
            self.profile_dict = json.loads(f.read())

    def test_not_given(self):
        profile = Profile('TEST', self.profile_dict)
        bag = bagit.Bag(self.bagdir)
        result = profile.validate(bag)
        self.assertTrue(result)

    def test_required_not_allowed(self):
        self.profile_dict["Tag-Files-Allowed"] = []
        self.profile_dict["Tag-Files-Required"] = ['tag-foo']
        with open(join(self.bagdir, 'tag-foo'), 'w'): pass
        profile = Profile('TEST', self.profile_dict)
        result = profile.validate(bagit.Bag(self.bagdir))
        self.assertFalse(result)
        self.assertEqual(len(profile.report.errors), 1)
        self.assertTrue('Required tag files' in profile.report.errors[0].value)

    def test_existing_not_allowed(self):
        self.profile_dict["Tag-Files-Allowed"] = []
        with open(join(self.bagdir, 'tag-foo'), 'w'): pass
        profile = Profile('TEST', self.profile_dict)
        result = profile.validate(bagit.Bag(self.bagdir))
        self.assertFalse(result)
        self.assertEqual(len(profile.report.errors), 1)
        self.assertTrue("Existing tag file" in profile.report.errors[0].value)


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

    def test_report_after_validate(self):
        self.assertIsNone(self.profile.report)
        self.profile.validate(self.bag)
        self.assertTrue(self.profile.report.is_valid)

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

    def test_find_tag_files(self):
        expect = [join(os.getcwd(), 'fixtures/test-bar', f) for f in ['DPN/dpnFirstNode.txt', 'DPN/dpnRegistry']]
        self.assertEqual(sorted(find_tag_files(self.bag.path)), expect)

if __name__ == '__main__':
    main()
