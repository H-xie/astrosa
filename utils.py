# -*- coding: UTF-8 -*-
"""
@File    ：utils.py
@Author  ：heaven
@Date    ：2023/3/1 20:16 
"""
import pandas as pd
from astropy.coordinates import SkyCoord, EarthLocation
import astropy.units as u
from astropy.time import Time
from rich.progress import Progress, TimeElapsedColumn

from astroplan import FixedTarget
from astroplan import Schedule
from astroplan.observer import Observer


def df2Targets(df: pd.DataFrame):
    coord = SkyCoord(ra=df['_RAJ2000'] * u.deg,
                     dec=df['_DEJ2000'] * u.deg)

    star = FixedTarget(coord=coord, name=df['tyc2-id'])

    return star


location = EarthLocation(lat=43.82416667 * u.deg, lon=126.331111 * u.deg, height=313 * u.m)
observer = Observer(location)
observing_date = Time('2023-06-08')

obs_start = observer.twilight_evening_astronomical(time=observing_date, which='next')
obs_end = observer.twilight_morning_astronomical(time=obs_start, which='next')

def schedule2df_ex(schedule: Schedule):
    columns = ['name',
               'start',
               'end',
               'RA_ICRS_',
               'DE_ICRS_',
               'priority']

    schedule_df = pd.DataFrame(
        columns=columns)

    for slot in schedule.slots:
        if hasattr(slot.block, 'target'):
            start_times = slot.start.iso
            end_times = slot.end.iso
            target_names = slot.block.target.name
            ra = slot.block.target.ra.value
            dec = slot.block.target.dec.value
            # config = slot.block.configuration
            priority = slot.block.priority
        else:
            continue

        tmp = pd.Series([target_names, start_times, end_times, ra, dec, priority],
                        index=columns
                        )
        schedule_df = pd.concat([schedule_df, tmp.to_frame().T], ignore_index=True)
    schedule_df = schedule_df.infer_objects()
    schedule_df['name'] = schedule_df['name'].astype(str)
    schedule_df['start'] = schedule_df['start'].astype('datetime64')
    schedule_df['end'] = schedule_df['end'].astype('datetime64')

    schedule_df = schedule_df.sort_values('start')

    return schedule_df

def schedule2df(schedule: Schedule):
    progress = Progress(
        *Progress.get_default_columns(),
        TimeElapsedColumn()
    )

    columns = ['name',
               'start',
               'end',
               '_RAJ2000',
               '_DEJ2000',
               'priority',
               'configuration']
    with progress:
        task = progress.add_task('to file', total=len(schedule.slots))

        schedule_df = pd.DataFrame(
            columns=columns)

        for slot in schedule.slots:
            progress.update(task, advance=1)
            if hasattr(slot.block, 'target'):
                start_times = slot.start.iso
                end_times = slot.end.iso
                target_names = slot.block.target.name
                ra = slot.block.target.ra.value
                dec = slot.block.target.dec.value
                config = slot.block.configuration
                priority = slot.block.priority
            else:
                continue

            tmp = pd.Series([target_names, start_times, end_times, ra, dec, priority, config],
                            index=columns
                            )
            schedule_df = pd.concat([schedule_df, tmp.to_frame().T], ignore_index=True)
    schedule_df = schedule_df.infer_objects()
    schedule_df['name'] = schedule_df['name'].astype(str)
    schedule_df['start'] = schedule_df['start'].astype('datetime64')
    schedule_df['end'] = schedule_df['end'].astype('datetime64')

    schedule_df = schedule_df.sort_values('start')

    return schedule_df
