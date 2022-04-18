import get_shards
import numpy as np
from astropy.table import Table

_mins = []
_maxs = []

depths = [0, 1, 2, 3, 4, 5, 6]

for depth in depths:
    shards = get_shards.getShards(0.0, 0.0, 180.0, depth=depth)
    print(np.min(shards['shard']), np.max(shards['shard']))
    _mins.append(np.min(shards['shard']))
    _maxs.append(np.max(shards['shard']))

t = Table()
t['depth'] = depths
t['min'] = _mins
t['max'] = _maxs

min_pred = (4**(t['depth']+1))*2
max_pred = 2*min_pred - 1

print(np.sum(min_pred != t['min']))
print(np.sum(max_pred != t['max']))
