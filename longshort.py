import random

import astropy.units as u
import pandas as pd
from astroplan import FixedTarget
from astroplan import ObservingBlock, AirmassConstraint, AtNightConstraint, Schedule, SequentialScheduler
from astroplan import PriorityScheduler
from astroplan.plots import plot_schedule_airmass
from astropy.coordinates import SkyCoord
from sqlalchemy import create_engine

from utils import obs_start, obs_end, observer
from utils import observing_date

engine = create_engine('sqlite:///astrosa/data/astrosa.sqlite')
conn = engine.connect()
date_string = observing_date.strftime("%Y_%m_%d_%H_%M_%S")

# if long shot candidate table exists, read it
candidates_table_name = f"longshort_candidates_{date_string}"
try:
    candidates = pd.read_sql_table(candidates_table_name, con=conn)
    print(f"{candidates_table_name} already exists")
except ValueError:
    print(f"{candidates_table_name} not exists")
    candidates = pd.read_sql_table(f'candidate_{date_string}', con=conn)

    exposure_elapsed = [1, 2, 4, 6, 12]
    random.randint(0, 5)
    candidates['num_exposures'] = [exposure_elapsed[random.randint(0, 4)] for _ in range(len(candidates))]
    candidates['minutes_per_exposure'] = 5
    candidates['exposure_minutes'] = candidates['num_exposures'] * candidates['minutes_per_exposure']
    # save to db
    try:
        candidates.to_sql(candidates_table_name,
                          con=conn,
                          index=False)
    except ValueError:
        print(f"{candidates_table_name} already exists")

candidates_icrs = SkyCoord(ra=candidates.RA_ICRS_.to_numpy() * u.deg,
                           dec=candidates.DE_ICRS_.to_numpy() * u.deg,
                           frame='icrs')

# plot the priority versus exposure time， the scatter size is the count of the target

from matplotlib import pyplot as plt
import seaborn as sns

# count the number of targets in the same priority-exposure time pair
candidates['count'] = candidates.groupby(['priority', 'num_exposures'])['priority'].transform('count')

# plot priority versus exposure time, the scatter size is the count of the target
sns.scatterplot(data=candidates, x='priority', y='num_exposures', size='count', hue='count')

# set legend outside the plot
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# create observing blocks. The time per exposure is 5 minutes
blocks = []
for star, name, p, (_, v) in zip(candidates_icrs,
                                 candidates.ID,
                                 candidates.priority,
                                 candidates.iterrows()):
    target = FixedTarget(coord=star, name=name)

    # b = ObservingBlock(target, v.num_exposures * u.min, priority=p)
    b = ObservingBlock.from_exposures(target, p, 5 * u.min, v.num_exposures)
    blocks.append(b)

    print(star, v.rise_time, p)

# create the scheduler
from astrosa.assess import Transitioner

# create the list of constraints that all targets must satisfy
global_constraints = [AirmassConstraint(max=3, boolean_constraint=False),
                      AtNightConstraint.twilight_astronomical()]

transitioner = Transitioner([6 * u.deg / u.second, 6 * u.deg / u.second],
                            [1 * u.deg / u.second ** 2, 1 * u.deg / u.second ** 2],
                            instrument_reconfig_times={'filter':
                                                           {('B', 'G'): 10 * u.second,
                                                            ('G', 'R'): 10 * u.second,
                                                            'default': 30 * u.second}})

priority_scheduler = PriorityScheduler(constraints=global_constraints,
                                       observer=observer,
                                       transitioner=transitioner)
schedule_prio = Schedule(obs_start, obs_end)
priority_scheduler(blocks, schedule_prio)

seq_scheduler = SequentialScheduler(constraints=global_constraints,
                                    observer=observer,
                                    transitioner=transitioner)

schedule_seq = Schedule(obs_start, obs_end)
seq_scheduler(blocks, schedule_seq)

# plot the schedule
plot_schedule_airmass(schedule_prio)
plot_schedule_airmass(schedule_seq)

# save to db
from utils import schedule2df_ex

x = schedule2df_ex(schedule_seq)
x.to_sql(f"sequential_schedule_{date_string}_1115", con=conn, if_exists='replace', index=False)

x = schedule2df_ex(schedule_prio)
x.to_sql(f"priority_schedule_{date_string}_1115", con=conn, if_exists='replace', index=False)
