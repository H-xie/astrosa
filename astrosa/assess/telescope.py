#  Licensed under the MIT license - see LICENSE.txt
from typing import Tuple

import astropy.coordinates as coord
import astropy.time as atime
import astropy.units as u
from astropy.coordinates import AltAz, SkyCoord
from .slew import calculate_slew


class Mount:
    """
    望远镜转台

    速度，指向
    """

    def __init__(self, max_velocity: Tuple[None, None] = None,
                 max_acceleration: Tuple[None, None] = None,
                 current_pointing=None,
                 current_velocity=[0 * u.deg / u.second, 0 * u.deg / u.second]):
        self.max_velocity = max_velocity
        self.max_acceleration = max_acceleration

        self.current_pointing = current_pointing
        self.current_velocity = current_velocity

    def slew(self, target_pointing) -> tuple[bool, atime.TimeDelta]:
        """
        转向到目标指向
        速度曲线是正弦曲线

        Parameters
        ----------
        target_pointing :
            目标指向，可以是天球坐标，也可以是地平坐标

        Returns
        -------
        bool
            是否可以转到对应位置
        atime.TimeDelta
            转到对应位置所需时间
        """

        slew_time = [None, None]
        # calculate slew time, speed curve is a T curve
        t, a = calculate_slew(self.current_pointing.az,
                              target_pointing.az,
                              self.current_velocity[0],
                              self.max_velocity[0],
                              self.max_acceleration[0])
        slew_time[0] = t[-1]
        t, a = calculate_slew(self.current_pointing.alt,
                              target_pointing.alt,
                              self.current_velocity[1],
                              self.max_velocity[1],
                              self.max_acceleration[1])
        slew_time[1] = t[-1]

        longest_time = max(slew_time)
        time_space = target_pointing.obstime - self.current_pointing.obstime
        if longest_time <= time_space:
            return True, longest_time
        else:
            return False, longest_time

    def __str__(self):
        result = f"Mount:\n\tmax_velocity: {self.max_velocity}\n\tmax_acceleration: {self.max_acceleration}\n\t" \
                 f"current_pointing: {self.current_pointing}\n\tcurrent_velocity: {self.current_velocity}"
        return result


class Terminal:

    def __init__(self, camera_filter, camera, configure_time):
        """
        终端设备的切换所需时间
        Parameters
        ----------
        camera_filter : 默认的camera_filter "none"
        camera :
        configure_time : 是一个字典，key1 -> value[key2] 是 key1 状态到 key2 状态所需的时间
        """
        self.camera_filter = camera_filter
        self.camera = camera

        self.configure_time: dict = configure_time

        self.configure_set: set = self._create_configure_set(configure_time)

        if not self._check_configure():
            raise ValueError(f"configure is not valid, {self.camera_filter} or {self.camera} is not in configure_time")

    def set_to(self,
               camera_filter: str,
               camera: str) -> atime.TimeDelta | None:
        """
        set congifure,
        if configure is same, return 0
        if current -> to_be_set is not in configure_time, check reversely


        Parameters
        ----------
        camera_filter :
        camera :

        Returns
        -------

        """
        result = 0 * u.second

        def check_out(key1, key2) -> atime.TimeDelta | None:
            """
            if key1 is in configure_time, check if key2 is in configure_time[key1]
            if key1 is not in configure_time, switch key1 and key2

            Parameters
            ----------
            key1 :
            key2 :

            Returns
            -------

            """
            if key1 not in self.configure_set:
                print(f"{key1} is not in configure_set")
                return None
            if key2 not in self.configure_set:
                print(f"{key2} is not in configure_set")
                return None

            if key1 == key2:
                return 0 * u.second

            elif key1 in self.configure_time:
                result = self.configure_time[key1].get(key2, None)
                if result is None and key2 in self.configure_time:
                    return self.configure_time[key2].get(key1, None)
                else:
                    return result
            else:
                print(f"can't find conversion:  {key1} - {key2} in configure_time")
                return None

        if self.camera_filter != camera_filter:
            check_result = check_out(self.camera_filter, camera_filter)
            if check_result is not None:
                result += check_result
                self.camera_filter = camera_filter
            else:
                print(f"can't set {self.camera_filter} to {camera_filter}")
                return None

        if self.camera != camera:
            check_result = check_out(self.camera, camera)
            if check_result is not None:
                result += check_result
                self.camera = camera
            else:
                print(f"can't set {self.camera} to {camera}")
                return None

        return result

    def _create_configure_set(self, configure_time):
        """
        collect keys in configure_time as a set to identify valid configure.

        Parameters
        ----------
        configure_time :

        Returns
        -------

        """
        configure_set = set()
        for key1 in configure_time.keys():
            configure_set.add(key1)
            for key2 in configure_time[key1].keys():
                configure_set.add(key2)
        return configure_set

    def _check_configure(self):
        return self.camera_filter in self.configure_set and self.camera in self.configure_set

    def __str__(self):
        result = f"Terminal:\n\tcamera_filter: {self.camera_filter}\n\tcamera: {self.camera}\n\t" \
                 f"configure_time: {self.configure_time}"
        return result


class Telescope:
    """
    望远镜
    包含转台，终端设备

    可以用转台的初始化参数初始化，也可以用实例初始化
    """

    def __init__(self,
                 max_velocity: Tuple = None,
                 max_acceleration: Tuple = None,
                 current_pointing: AltAz = None,
                 current_velocity: Tuple = None,
                 camera_filter: str = None,
                 camera: str = None,
                 configure_time: dict[str, dict] = None,
                 mount: Mount = None,
                 terminal: Terminal = None):
        # check parameters. mount and terminal versus others cannot be both None
        is_object = mount is not None and terminal is not None
        is_parameters = (max_velocity is not None)
        is_parameters = is_parameters and (max_acceleration is not None)
        is_parameters = is_parameters and (current_pointing is not None)
        is_parameters = is_parameters and (current_velocity is not None)
        is_parameters = is_parameters and (camera_filter is not None)
        is_parameters = is_parameters and (camera is not None)
        is_parameters = is_parameters and (configure_time is not None)

        if (is_parameters and is_object) or (not (is_parameters or is_object)):
            raise ValueError(
                f"Should give either every parameters or (mount and terminal) objects. Don't give both in the same time."
                f"object:{not is_object}, parameters:{not is_parameters}")

        elif is_object:
            self.mount = mount
            self.terminal = terminal

        else:
            self.mount = Mount(max_velocity, max_acceleration, current_pointing, current_velocity)
            self.terminal = Terminal(camera_filter, camera, configure_time)

    def slew(self, target_pointing: AltAz) -> tuple[bool, atime.TimeDelta]:
        """
        target pointing can only be AltAz

        Parameters
        ----------
        target_pointing :

        Returns
        -------

        """
        return self.mount.slew(target_pointing)

    def set_to(self,
               camera_filter: str,
               camera: str) -> atime.TimeDelta | None:
        return self.terminal.set_to(camera_filter, camera)

    def __str__(self):
        result = f"Telescope:\n\tmount: {self.mount}\n\tterminal: {self.terminal}"
        return result


    # bring all mount properties to telescope
    @property
    def current_pointing(self):
        return self.mount.current_pointing

    @property
    def current_velocity(self):
        return self.mount.current_velocity

    @property
    def max_velocity(self):
        return self.mount.max_velocity

    @property
    def max_acceleration(self):
        return self.mount.max_acceleration

    # bring all terminal properties to telescope
    @property
    def camera_filter(self):
        return self.terminal.camera_filter

    @property
    def camera(self):
        return self.terminal.camera

    @property
    def configure_time(self):
        return self.terminal.configure_time


