# -*- coding: utf-8 -*-
# @Time    : 2023-02-02 002 12:47
# @Author  : H-XIE
from unittest import TestCase

import astroplan
from assess.core import *
import pandas as pd


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


class TestOssaf(TestCase):
    def test_ossaf(self):
        scheduler = Scheduler()

        # create Plan
        s = list()
        s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 16:00:00'), Time('2023-01-01 16:01:00')))
        s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 16:02:00'), Time('2023-01-01 16:03:00')))
        s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 16:06:00'), Time('2023-01-01 16:07:00')))

        plan = Plan()

        plan.data = s

        # create Cloud
        cloud = pd.read_json("data/cloud.json")
        time = Time('2023-01-01 16:00:00')
        weather = Weather(time, cloud)
        observer = astroplan.Observer.at_site("BAO")

        ossaf = Ossaf(observer, plan, scheduler, weather)

        self.assertIsNotNone(ossaf)
