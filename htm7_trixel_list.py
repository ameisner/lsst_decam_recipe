import get_shards

# 180 deg radius -> full sky
shards = get_shards.getShards(0.0, 0.0, 180.0, depth=7)

shards.write('htm7_trixel_list.fits', format='fits')
