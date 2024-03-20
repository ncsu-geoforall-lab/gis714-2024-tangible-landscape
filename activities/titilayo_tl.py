#!/usr/bin/env python3

import os

import grass.script as gs

def run_overlandflow(scanned_elev, env, **kwargs):
    gs.run_command("v.to.rast", input="streams@PERMANENT", output="rural_streams", use="val", val=1, flags="d")
    gs.run_command("r.lake.series", elevation="elev_lid792_1m", seed="rural_streams", start_water_level=104.0, end_water_level=114.0, water_level_step = 0.2, output="flooding")

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
