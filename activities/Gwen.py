#!/usr/bin/env python3

import os

import grass.script as gs

import numpy as np


def get_environment(**kwargs):
    """!Returns environment for running modules.
    All modules for which region is important should
    pass this environment into run_command or similar.
    @param tmp_regions a list of temporary regions
    @param kwargs arguments for g.region
    @return environment as a dictionary
    """
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"
    env["GRASS_VERBOSE"] = "0"
    env["GRASS_MESSAGE_FORMAT"] = "standard"
    region3d = False
    if "raster_3d" in kwargs:
        region3d = True
    env["GRASS_REGION"] = gs.region_env(region3d=region3d, **kwargs)
    return env


# change detection from analyses.py
def change_detection(
    before,
    after,
    change,
    height_threshold,
    cells_threshold,
    add,
    max_detected,
    debug,
    env,
):
    diff_thr = "diff_thr_" + str(uuid.uuid4()).replace("-", "")
    diff_thr_clump = "diff_thr_clump_" + str(uuid.uuid4()).replace("-", "")
    coeff = gs.parse_command(
        "r.regression.line", mapx=after, mapy=before, flags="g", env=env
    )
    gs.mapcalc(
        "diff = {a} + {b} * {after} - {before}".format(
            a=coeff["a"], b=coeff["b"], before=before, after=after
        ),
        env=env,
    )
    try:
        if add:
            gs.mapcalc(
                "{diff_thr} = if(({a} + {b} * {after} - {before}) > {thr1} &&"
                " ({a} + {b} * {after} - {before}) < {thr2}, 1, null())".format(
                    a=coeff["a"],
                    b=coeff["b"],
                    diff_thr=diff_thr,
                    after=after,
                    before=before,
                    thr1=height_threshold[0],
                    thr2=height_threshold[1],
                ),
                env=env,
            )
        else:
            gs.mapcalc(
                "{diff_thr} = if(({before} - {a} + {b} * {after}) > {thr}, 1, null())".format(
                    diff_thr=diff_thr,
                    a=coeff["a"],
                    b=coeff["b"],
                    after=after,
                    before=before,
                    thr=height_threshold,
                ),
                env=env,
            )

        gs.run_command(
            "r.clump", input=diff_thr, output=diff_thr_clump, env=env
        )
        stats = (
            gs.read_command(
                "r.stats",
                flags="cn",
                input=diff_thr_clump,
                sort="desc",
                env=env,
            )
            .strip()
            .splitlines()
        )
        if debug:
            print("DEBUG: {}".format(stats))
        if len(stats) > 0 and stats[0]:
            cats = []
            found = 0
            for stat in stats:
                if found >= max_detected:
                    break
                if (
                    float(stat.split()[1]) < cells_threshold[1]
                    and float(stat.split()[1]) > cells_threshold[0]
                ):  # larger than specified number of cells
                    found += 1
                    cat, value = stat.split()
                    cats.append(cat)
            if cats:
                rules = ["{c}:{c}:1".format(c=c) for c in cats]
                gs.write_command(
                    "r.recode",
                    input=diff_thr_clump,
                    output=change,
                    rules="-",
                    stdin="\n".join(rules),
                    env=env,
                )
                gs.run_command(
                    "r.volume",
                    flags="f",
                    input=change,
                    clump=diff_thr_clump,
                    centroids=change,
                    env=env,
                )
            else:
                gs.warning("No change found!")
                gs.run_command("v.edit", map=change, tool="create", env=env)
        else:
            gs.warning("No change found!")
            gs.run_command("v.edit", map=change, tool="create", env=env)

        gs.run_command(
            "g.remove",
            flags="f",
            type=["raster"],
            name=[diff_thr, diff_thr_clump],
            env=env,
        )
    except:
        gs.run_command(
            "g.remove",
            flags="f",
            type=["raster"],
            name=[diff_thr, diff_thr_clump],
            env=env,
        )


def run_distance(real_elev, scanned_elev, env, **kwargs):
    # not sure what shifting this does?
    env2 = get_environment(
        raster=scanned_elev, n="n-100", s="s+100", e="e-100", w="w+100"
    )
    before = "scan_saved"

    # get new garden location points from pins
    change_detection(
        before=before,
        after=scanned_elev,
        change="change",
        height_threshold=[15, 100],
        cells_threshold=[5, 100],
        add=True,
        max_detected=13,
        debug=True,
        env=env2,
    )
    # dict of new points
    points = {}
    gs.run_command("v.edit", tool="create", map=trail, env=env)
    # detected points
    points_raw = (
        gs.read_command(
            "v.out.ascii", input="change", type="point", format="point"
        )
        .strip()
        .split()
    )
    i = 0
    for point in points_raw:
        point = point.split("|")
        point = (float(point[0]), float(point[1]))
        points[i] = point
        i += 1

    # calculate shortest distance between points (replace this with least cost path later)
    dist_matrix = gs.read_command("v.net.allpairs", input=trail)
    shortest_dist = np.matrix.min(dist_matrix)

    # display the length of this shortest distance
    return shortest_dist


def main():
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"
    elevation = "elev_lid792_1m"
    elev_resampled = "elev_resampled"
    gs.run_command("g.region", raster=elevation, res=4, flags="a", env=env)
    gs.run_command(
        "r.resamp.stats", input=elevation, output=elev_resampled, env=env
    )

    run_distance(real_elev=elevation, scanned_elev=elev_resampled, env=env)


if __name__ == "__main__":
    main()
