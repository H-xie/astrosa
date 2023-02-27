import pandas as pd
from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy.time import Time

from astroplan import Observer, AirmassConstraint, AtNightConstraint, Transitioner, SequentialScheduler, Schedule, \
    TimeConstraint, Target, ObservingBlock, FixedTarget
from rich.progress import Progress, track

observer = Observer.at_site('BAO')
day = Time('2023-01-01')
obs_start = observer.twilight_evening_astronomical(time=day, which='next')
obs_end = observer.twilight_morning_astronomical(time=obs_start, which='next')

N_target = 2539913


# tyc2 = pd.read_json('assess/tests/data/tyc2-records.json', lines=True, chunksize=100)
# N = len(tyc2)
# print(f'tyc2 has {N} rows')


def make_tyc2_json():
    tyc2 = fits.open("assess/tests/data/tyc2.fit")

    tyc2_rows = tyc2[1]._nrows

    tyc2_dict = {}

    for i in range(tyc2_rows):
        data = tyc2[1].data[i]
        # ID
        tycid = data[3:6]
        tycid_str = f"TYC {tycid[0]}-{tycid[1]}-{tycid[2]}"

        # ra J2000
        ra = data['_RAJ2000']

        # dec J2000
        dec = data['_DEJ2000']

        # 视星等 V
        VTmag = data['VTmag']

        record = [ra, dec, VTmag]
        tyc2_dict[tycid_str] = record

        # print(tycid_str, record)

    df = pd.DataFrame.from_dict(tyc2_dict, orient='index', columns=['_RAJ2000', '_DEJ2000', 'VTmag'])
    df.to_json('assess/tests/data/tyc2.json')


def make_plan(obs_time, observer: Observer):
    #
    # create the list of constraints that all targets must satisfy
    global_constraints = [AirmassConstraint(max=3, boolean_constraint=False),
                          AtNightConstraint.twilight_civil()]

    slew_rate = .8 * u.deg / u.second
    transitioner = Transitioner(slew_rate,
                                {'filter': {('B', 'G'): 10 * u.second,
                                            ('G', 'R'): 10 * u.second,
                                            'default': 30 * u.second}})

    # Initialize the sequential scheduler with the constraints and transitioner
    seq_scheduler = SequentialScheduler(constraints=global_constraints,
                                        observer=observer,
                                        transitioner=transitioner)
    # Initialize a Schedule object, to contain the new schedule
    sequential_schedule = Schedule(obs_time[0], obs_time[1])

    # create observing block

    # load json
    tyc2 = pd.read_json('assess/tests/data/tyc2.json')
    N = 10
    print(f'tyc2 has {N} rows')

    # block
    blocks = []
    time_constraint = TimeConstraint(obs_time[0], obs_time[1])
    read_out = 20 * u.second
    nExposure = 16

    with Progress() as progress:
        task = progress.add_task("create blocks", total=N)

        i = 0
        for index, d in tyc2.iterrows():
            # print(type(d), d)
            # print(d['VTmag'])

            coord = SkyCoord(ra=d['_RAJ2000'].values * u.deg,
                             dec=d['_DEJ2000'].values * u.deg)
            star = FixedTarget(coord=coord,
                               name=index)

            b = ObservingBlock.from_exposures(star, 1, 60 * u.second, nExposure, read_out)

            blocks.append(b)
            i = i + 1
            # print(f'{i}/{N}')
            progress.update(task, advance=1)

            if i == N:
                break

    print('block filled')

    # Call the schedule with the observing blocks and schedule to schedule the blocks
    seq_scheduler(blocks, sequential_schedule)

    return sequential_schedule


def pick_target():
    with pd.read_json('assess/tests/data/tyc2-records.json', lines=True, chunksize=100) as reader:
        for chunk in reader:
            coord = SkyCoord(ra=chunk['_RAJ2000'].values * u.deg,
                             dec=chunk['_DEJ2000'].values * u.deg)

            star = FixedTarget(coord=coord, name=chunk['tyc2-id'].values)

            chunk['rise_time'] = observer.target_rise_time(obs_start, star, which='next')

    # for i in track(range(N)):
    #     d = tyc2.iloc[i]
    #     coord = SkyCoord(ra=d['_RAJ2000'] * u.deg,
    #                      dec=d['_DEJ2000'] * u.deg)
    #     star = FixedTarget(coord=coord,
    #                        name=tyc2.index[i])
    #
    #     star_rise_time = observer.target_rise_time(obs_start, star, which='next')
    #     star_set_time = observer.target_set_time(obs_start, star, which='next')
    #
    #     if star_rise_time < obs_end:
    #         print(f'{star.name} is ok')
    #     else:
    #         print(f'{star.name} cannot be seen.')

def get_rise_time():
    chunksize = 100
    f = open('tyc2-rise-BAO.json', 'a')
    with Progress() as progress:
        task = progress.add_task("create blocks", total=N_target / chunksize)

        with pd.read_json('assess/tests/data/tyc2-records.json', lines=True, chunksize=chunksize) as reader:
            for chunk in reader:
                coord = SkyCoord(ra=chunk['_RAJ2000'].values * u.deg,
                                 dec=chunk['_DEJ2000'].values * u.deg)

                star = FixedTarget(coord=coord, name=chunk['tyc2-id'].values)

                chunk['rise_time'] = observer.target_rise_time(obs_start, star, which='next').to_value('iso')


                chunk.to_json(f, orient='records', lines=True)

                progress.update(task, advance=1)
                # break

# 判断是否在天亮前升起.
chunksize = 1000000
visible_star = pd.DataFrame()
with Progress() as progress:
    task = progress.add_task("find visible target", total=N_target / chunksize)

    with pd.read_json('assess/tests/data/tyc2-rise.1791042.json', lines=True, chunksize=chunksize) as reader:
        for chunk in reader:
            vt = chunk[chunk['rise_time'].values < obs_end]

            if len(visible_star) ==0:
                visible_star = vt
            else:
                visible_star= pd.concat([visible_star, vt])

            progress.update(task, advance=1)

            # break

visible_star.to_json('tycho2-visible.864935.json', orient='records', lines=True)
