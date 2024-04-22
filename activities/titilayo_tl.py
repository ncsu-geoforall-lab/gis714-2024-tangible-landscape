#!/usr/bin/env python3

import os

import grass.script as gs

def run_overlandflow(scanned_elev, env, **kwargs):
<<<<<<< HEAD
    gs.run_command("r.watershed", elevation=scanned_elev, threshold=5000, accumulation="accum", drainage="drainage_direction", stream="streams", flags="a", env=env)
    gs.run_command("r.lake.series", elevation=scanned_elev, seed="streams", start_water_level=104, end_water_level=114, water_level_step=0.5, output="flooding", env=env)
=======
    gs.run_command("r.watershed", elevation=scanned_elev, threshold=5000, accumulation="accum", drainage="drainage_direction", stream="streams", flags="a")
    gs.run_command("r.lake.series", elevation=scanned_elev, seed="streams", start_water_level=104, end_water_level=114, water_level_step=0.5, output="flooding")
>>>>>>> 688e9cc59939a819a0cd114aee9672be450cb313

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
