# -*- coding: utf-8 -*-
# @Time    : 2023-02-02 002 12:47
# @Author  : H-XIE
from unittest import TestCase
from assess.core import *


class TestShot(TestCase):

    def setUp(self) -> None:
        self.shot = Shot(
            FixedTarget.from_name('Vega'),
            Time('2023-01-01 16:00:00'),
            Time('2023-01-01 16:01:00')
        )

    def test_target(self):
        # self.assertEqual(self.shot.target.name, 'Vega')
        self.assertEqual(self.shot.target, FixedTarget.from_name('Vega'))

    def test_start_time(self):
        self.assertEqual(self.shot.start_time, Time('2023-01-01 16:00:00'))

    def test_end_time(self):
        self.assertEqual(self.shot.end_time, Time('2023-01-01 16:01:00'))
