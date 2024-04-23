#!/usr/bin/env python3

import grass.script as gscript


def run_difference(base_elev, scanned_elev, env, **kwargs):
    regression_params = gscript.parse_command(
        "r.regression.line", flags="g", mapx=scanned_elev, mapy=base_elev, env=env
    )
    gscript.mapcalc(
        "{regression} = {a} + {b} * {before}".format(
            a=regression_params["a"],
            b=regression_params["b"],
            before=scanned_elev,
            regression="regression",
        ),
        env=env,
    )

    gscript.mapcalc(
        "{difference} = {regression} - {after}".format(
            regression="regression", after=base_elev, difference="diff"
        ),
        env=env,
    )

    gscript.write_command(
        "r.colors",
        map="diff",
        rules="-",
        stdin="-100 black\n-20 red\n0 white\n20 blue\n100 black",
        env=env,
    )


def simulate_fire_spotting(difference_layer, spotting_threshold, env):
    gscript.mapcalc(
        "{hotspots} = if({difference} > {threshold}, 1, null())".format(
            difference=difference_layer,
            hotspots="fire_hotspots",
            threshold=spotting_threshold,
        ),
        env=env,
    )

    gscript.run_command("d.rast", map="fire_hotspots", env=env)


def main():
    env = gscript.gisenv()
    # Updated layer names
    base_elev = "base_elevation_layer"
    scanned_elev = "scanned_elevation"
    spotting_threshold = 1  # The threshold for fire spotting
    run_difference(base_elev, scanned_elev, env)
    simulate_fire_spotting("diff", spotting_threshold, env)


if __name__ == "__main__":
    main()
