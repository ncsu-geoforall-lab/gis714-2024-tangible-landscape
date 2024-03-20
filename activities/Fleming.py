#!/usr/bin/env python3

import os
import grass.script as gs


def run_create_hog_lagoon(env):
    lagoon_centroid = "638550,220550"
    gs.write_command(
        "v.in.ascii",
        input="-",
        output="hog_lagoon_centroid",
        stdin=lagoon_centroid,
        format="point",
        separator=",",
        env=env,
    )
    gs.run_command(
        "v.buffer",
        input="hog_lagoon_centroid",
        output="hog_lagoon",
        distance=50,
        env=env,
    )


def run_lake(scanned_elev, env, **kwargs):
    coordinates = "638830,220150"
    gs.run_command(
        "r.lake",
        elevation=scanned_elev,
        lake="output_lake",
        coordinates=coordinates,
        water_level=120,
        env=env,
    )


def main():
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"
    elevation = "elev_lid792_1m"
    elev_resampled = "elev_resampled"
    gs.run_command("g.region", raster=elevation, res=4, flags="a", env=env)
    gs.run_command(
        "r.resamp.stats", input=elevation, output=elev_resampled, env=env
    )
    run_lake(scanned_elev=elev_resampled, env=env)
    run_create_hog_lagoon(env)


if __name__ == "__main__":
    main()
