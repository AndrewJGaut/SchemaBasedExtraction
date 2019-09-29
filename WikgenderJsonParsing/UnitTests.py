'''
Wikigender format:
{
'train':
 [ {
    entity1: NAME,
    relations: [
        {
            name: spouse,
            entity2: NAME,
            sentences: [
            ]
        }

    ]
} ],
'dev' : [ {
    entity1: NAME,
    relations: [
        {
            name: spouse,
            entity2: NAME,
            sentences: [
            ]
        }

    ]
}, ... ], ...
}
'''
from __future__ import absolute_import
import unittest

from DebiasJsonDataset import *


class UnitTests(unittest.TestCase):
    def test_json_genderswap(self):
        self.maxDiff = None

        # set up test data
        input_data = {
            'train': [
                {
                    'entity1': 'test1',
                    'relations': [
                        {
                            'relation_name': 'spouse',
                            'entity2': 'Johnny',
                            'sentences': [
                                'Johnny and his mother were talking to her father on the sister.'
                            ]
                        }

                    ]
                }
            ],
            'dev': [

            ],
            'male_test': [

            ],
            'female_test': [

            ]
        }

        expected_output = {
            'train': [
                {
                    'entity1': 'test1',
                    'relations': [
                        {
                            'relation_name': 'spouse',
                            'entity2': 'Johnny',
                            'sentences': [
                                'Johnny and her father were talking to his mother on the brother.'
                            ]
                        }

                    ]
                }
            ],
            'dev': [

            ],
            'male_test': [

            ],
            'female_test': [

            ]
        }

        print(json.dumps(createGenderSwappedDatasetEntries(input_data)))
        self.assertEqual(createGenderSwappedDatasetEntries(input_data), expected_output)


    def testJsonNameAnonynize(self):
        pass
