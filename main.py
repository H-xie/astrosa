from assess import *

import astroplan

# scheduler = Scheduler()

# create Plan
s = list()
s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 16:00:00'), Time('2023-01-01 16:01:00')))
s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 16:02:00'), Time('2023-01-01 16:03:00')))
s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 16:06:00'), Time('2023-01-01 16:07:00')))

plan = Plan()

plan.data = s

if plan.is_valid():
    print(f'plan is valid')

# create Cloud
cloud = pd.read_json("assess/tests/data/cloud.json")
weather = Weather(Cloud(cloud))
observer = astroplan.Observer.at_site("BAO")

ossaf = Ossaf(observer, plan, None, weather)

print("end")