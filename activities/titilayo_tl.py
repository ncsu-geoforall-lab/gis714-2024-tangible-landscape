#!/usr/bin/env python3

import os
import grass.script as gs

def overland_flow(input_points, water_level, env, **kwargs):    
    gs.run_command("v.surf.rst", input=input_points, elevation="elev_lid792_2m", tension=15, smooth=1.5, npmin=150,flags="d")
    gs.run_command("r.lake", elevation="elev_lid792_2m", water_level=water_level, lake="flood", coordinates="638728,220278", env=env)

def main():
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"
    input_points = "elev_lid792_bepts"

    region = "rural_1m"
    gs.run_command("g.region", region=region, flags="a", env=env)

    overland_flow(input_points=input_points, water_level=114.0, env=None)

if __name__ == "__main__":
    main()
