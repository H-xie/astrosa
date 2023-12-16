from astrosa.assess import FixedTarget
from astrosa.assess.metrics import RatioToBestAirmass
from utils import obs_start, observer


def test_ratio_to_best():
    polaris = FixedTarget.from_name('Vega')
    polaris_rise_time = observer.target_rise_time(obs_start, polaris)
    score = RatioToBestAirmass.from_target(observer, polaris_rise_time, polaris)
    print (f'score: {score}')

