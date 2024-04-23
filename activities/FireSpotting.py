#!/usr/bin/env python3

"""
Instructions


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
        points = "fire_points"
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

    simulate_fire_spotting(points, env)


def simulate_fire_spotting(point_map, env, spotting_distance=100):
    """
    Simulates fire spotting by creating additional points around fire origin points.
    """
    gs.run_command(
        "v.buffer",
        input=point_map,
        output="fire_spotting_areas",
        distance=spotting_distance,
        env=env,
    )
    gs.run_command(
        "v.random",
        output="new_fire_spots",
        npoints=10,
        restrict="fire_spotting_areas",
        env=env,
    )


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
    points = "fire_points"
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
