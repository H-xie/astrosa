from rich.progress import Progress, TimeElapsedColumn, track

import astroplan
from assess import *
from utils import df2Targets

# scheduler = Scheduler()

# create Plan
s = list()
s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 19:00:00'), Time('2023-01-01 19:01:00')))
s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 19:02:00'), Time('2023-01-01 19:03:00')))
s.append(Shot(FixedTarget.from_name('Vega'), Time('2023-01-01 19:06:00'), Time('2023-01-01 19:07:00')))

asp_priority_plan = pd.read_json('assess/tests/data/schedule_140of300.json')

# DataFrame 2 plan
for _, star in track(asp_priority_plan.iterrows()):
    star_target = df2Targets(star)
    start = Time(star['start'])
    end = Time(star['end'])

    vt_mag = star['VTmag'] * u.mag

    shot = Shot(star_target, start, end)

    break  # for debug

plan = Plan()

plan.data = s

if plan.is_valid():
    print(f'plan is valid')

# create Cloud
cloud = pd.read_json("assess/tests/data/cloud.json")
weather = Weather(Cloud(cloud))
observer = astroplan.Observer.at_site("BAO")

ossaf = Ossaf(observer, plan, None, weather)

result = ossaf.run()

print(result)

print("end")
