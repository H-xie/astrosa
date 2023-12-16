from astroplan import FixedTarget
from astroplan import Observer
from astroplan import ObservingBlock
from astroplan.constraints import AtNightConstraint, AirmassConstraint
from astroplan.constraints import TimeConstraint
from astroplan.scheduling import Schedule
from astroplan.scheduling import SequentialScheduler
from astrosa.assess import Transitioner
from astropy import units as u
from astropy.time import Time

apo = Observer.at_site('apo')

# Initialize the targets
deneb = FixedTarget.from_name('Deneb')
m13 = FixedTarget.from_name('M13')

noon_before = Time('2016-07-06 19:00')
noon_after = Time('2016-07-07 19:00')

# create the list of constraints that all targets must satisfy
global_constraints = [AirmassConstraint(max=3, boolean_constraint=False),
                      AtNightConstraint.twilight_civil()]

# Define the read-out time, exposure duration and number of exposures
read_out = 20 * u.second
deneb_exp = 60 * u.second
m13_exp = 100 * u.second
n = 16
blocks = []

half_night_start = Time('2016-07-07 02:00')
half_night_end = Time('2016-07-07 08:00')
first_half_night = TimeConstraint(half_night_start, half_night_end)
# Create ObservingBlocks for each filter and target with our time
# constraint, and durations determined by the exposures needed
for priority, bandpass in enumerate(['B', 'G', 'R']):
    # We want each filter to have separate priority (so that target
    # and reference are both scheduled)
    b = ObservingBlock.from_exposures(deneb, priority, deneb_exp, n, read_out,
                                      configuration={'filter': bandpass},
                                      constraints=[first_half_night])
    blocks.append(b)
    b = ObservingBlock.from_exposures(m13, priority, m13_exp, n, read_out,
                                      configuration={'filter': bandpass},
                                      constraints=[first_half_night])
    blocks.append(b)


def test_transition():
    # Initialize a transitioner object with the slew rate and/or the
    # duration of other transitions (e.g. filter changes)
    transitioner = Transitioner(max_velocity=[6 * u.deg / u.second, 6 * u.deg / u.second],
                                max_accelartion=[1 * u.deg / u.second ** 2, 1 * u.deg / u.second ** 2],
                                instrument_reconfig_times={'filter': {('B', 'G'): 10 * u.second,
                                                                      ('G', 'R'): 10 * u.second,
                                                                      'default': 30 * u.second}})

    # Initialize the sequential scheduler with the constraints and transitioner
    seq_scheduler = SequentialScheduler(constraints=global_constraints,
                                        observer=apo,
                                        transitioner=transitioner)
    # Initialize a Schedule object, to contain the new schedule
    sequential_schedule = Schedule(noon_before, noon_after)

    # Call the schedule with the observing blocks and schedule to schedule the blocks
    seq_scheduler(blocks, sequential_schedule)

    print(sequential_schedule.to_table())
