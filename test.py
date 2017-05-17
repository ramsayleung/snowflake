#!/usr/bin/env python3
# # -*- coding: utf-8 -*-
# author:Samray <samrayleung@gmail.com>

import unittest

from id_generator import IdGenerator


class TestIdGenerator(unittest.TestCase):
    def test_id_is_unique(self):
        id_generator = IdGenerator()
        ids = set()
        id_number = 1000000
        for i in range(id_number):
            ids.add(id_generator.generate_id())
        self.assertEqual(id_number, len(ids))


if __name__ == '__main__':
    unittest.main()
