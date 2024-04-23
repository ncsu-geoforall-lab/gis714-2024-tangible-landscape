#!/usr/bin/env python3


import os

import grass.script as gs


def run_overlandflow(scanned_elev, env, **kwargs):
    # generate a stream from the elevation map
    # use the stream as the seed for the r.lake.series

    gs.run_command(
        "r.watershed",
        elevation=scanned_elev,
        threshold=5000,
        accumulation="accum",
        drainage="drainage_direction",
        stream="streams",
        flags="a",
        env=env,
    )
    gs.run_command(
        "r.lake.series",
        elevation=scanned_elev,
        seed="streams",
        start_water_level=104,
        end_water_level=114,
        water_level_step=0.5,
        output="flooding",
        env=env,
    )


def main():
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"
    elevation = "elev_lid792_1m"
    elev_resampled = "elev_resampled"
    gs.run_command("g.region", raster=elevation, res=4, flags="a", env=env)
    gs.run_command("r.resamp.stats", input=elevation, output=elev_resampled, env=env)

    run_overlandflow(scanned_elev=elev_resampled, env=env)


if __name__ == "__main__":
    main()
