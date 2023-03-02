from rich.progress import Progress, TimeElapsedColumn, track

import astroplan
from assess import *
from utils import df2Targets

# scheduler = Scheduler()

# create Plan
s = list()

asp_priority_plan = pd.read_json('assess/tests/data/schedule_129of300.json')

# DataFrame 2 plan
for _, star in track(asp_priority_plan.iterrows()):
    star_target = df2Targets(star)
    start = Time(star['start'])
    end = Time(star['end'])

    vt_mag = star['VTmag'] * u.mag

    shot = Shot(star_target, start, end)
    s.append(shot)


plan = Plan()

plan.data = s

if plan.is_valid():
    print(f'plan is valid')

# create Cloud
cloud = pd.read_json("assess/tests/data/cloud.json", orient='index')
weather = Weather(Cloud(cloud))
observer = astroplan.Observer.at_site("BAO")

ossaf = Ossaf(observer, plan, None, weather)

result = ossaf.run()

print(result)

print("end")
