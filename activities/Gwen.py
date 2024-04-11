#!/usr/bin/env python3

"""
Instructions

- Functions intended to run for each scan
  need to start with `run_`, e.g., `run_slope`.

- Do not modify the parameters of the `run_` function
  unless you know what you are doing.
  See optional parameters at:
  https://github.com/tangible-landscape/grass-tangible-landscape/wiki/Running-analyses-and-developing-workflows#python-workflows

- All gs.run_command/read_command/write_command/parse_command
  need to be passed *env* parameter like this: `(..., env=env)`.
"""

import os

import grass.script as gs


def run_function_with_points(scanned_elev, env, points=None, **kwargs):
    """Doesn't do anything, except loading points from a vector map to Python

    If *points* is provided, the function assumes it is name of an existing vector map.
    This is used during testing.
    If *points* is not provided, the function assumes it runs in Tangible Landscape.
    """
    if not points:
        # If there are no points, ask Tangible Landscape to generate points from
        # a change in the surface.
        points = "points"
        import analyses

        analyses.change_detection(
            "scan_saved",
            scanned_elev,
            points,
            height_threshold=[10, 100],
            cells_threshold=[5, 50],
            add=True,
            max_detected=5,
            debug=True,
            env=env,
        )

    # generate random point for focal garden
    gs.run_command("v.random", output=focal_garden, npoints=1, seed=3)
    
    # calculate the cost surface
    gs.run_command("r.cost", input="cfactorgrow_1m", output=cost_surface, start_points=focal_garden, stop_points=points)
    
    #calculate connectivity metric
    data = gs.read_command("r.what", map=cost_surface, points=points)
    data_lines = data.splitlines()
    data = data_lines.split('|')
    i = 3
    connectivity = 0 
    for datum in data:
        connectivity += 1/data[i]
        i += 3

    # display the connectivity metric
    event = updateDisplay(value=connectivity) 
    eventHandler.postEvent(receiver=eventHandler.activities_panel, event=event



def main():
    """Function which runs when testing without Tangible Landscape"""

    # No need to edit this block. It should stay the same.
    # Get the current environment variables as a copy.
    env = os.environ.copy()
    # We want to run this repetitively and replace the old data by the new data.
    env["GRASS_OVERWRITE"] = "1"
    elevation = "elev_lid792_1m"
    elev_resampled = "elev_resampled"
    # We use resampling to get a similar resolution as with Tangible Landscape.
    gs.run_command("g.region", raster=elevation, res=4, flags="a", env=env)
    gs.run_command("r.resamp.stats", input=elevation, output=elev_resampled, env=env)
    # The end of the block which needs no editing.

    # Code specific to testing of the analytical function.
    # Create points which is the additional input needed for the process.
    points = "points"
    gs.write_command(
        "v.in.ascii",
        flags="t",
        input="-",
        output=points,
        separator="comma",
        stdin="638432,220382\n638621,220607",
        env=env,
    )
    # Call the analysis.
    run_function_with_points(scanned_elev=elev_resampled, env=env, points=points)


if __name__ == "__main__":
    main()
