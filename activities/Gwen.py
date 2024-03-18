#!/usr/bin/env python3

import os

import grass.script as gs

import numpy as np

#change detection from analyses.py
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
    coeff = gcore.parse_command(
        "r.regression.line", mapx=after, mapy=before, flags="g", env=env
    )
    grast.mapcalc(
        "diff = {a} + {b} * {after} - {before}".format(
            a=coeff["a"], b=coeff["b"], before=before, after=after
        ),
        env=env,
    )
    try:
        if add:
            grast.mapcalc(
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
            grast.mapcalc(
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

        gcore.run_command("r.clump", input=diff_thr, output=diff_thr_clump, env=env)
        stats = (
            gcore.read_command(
                "r.stats", flags="cn", input=diff_thr_clump, sort="desc", env=env
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
                gcore.write_command(
                    "r.recode",
                    input=diff_thr_clump,
                    output=change,
                    rules="-",
                    stdin="\n".join(rules),
                    env=env,
                )
                gcore.run_command(
                    "r.volume",
                    flags="f",
                    input=change,
                    clump=diff_thr_clump,
                    centroids=change,
                    env=env,
                )
            else:
                gcore.warning("No change found!")
                gcore.run_command("v.edit", map=change, tool="create", env=env)
        else:
            gcore.warning("No change found!")
            gcore.run_command("v.edit", map=change, tool="create", env=env)

        gcore.run_command(
            "g.remove",
            flags="f",
            type=["raster"],
            name=[diff_thr, diff_thr_clump],
            env=env,
        )
    except:
        gcore.run_command(
            "g.remove",
            flags="f",
            type=["raster"],
            name=[diff_thr, diff_thr_clump],
            env=env,
        )

def run_distance(real_elev, scanned_elev, env, **kwargs):
    env2 = get_environment(raster=scanned_elev, n='n-100', s='s+100', e='e-100', w='w+100') # not sure what shifting this does?   
    before = 'scan_saved' #shouldn't this be real_elev?
    
    # get new garden location points from pins
    change_detection(before=before, after=scanned_elev,
                              change='change', height_threshold=[15, 100], cells_threshold=[5, 100], add=True, max_detected=13, debug=True, env=env2)
    # dict of new points
    points = {}
    data = gs.read_command('v.out.ascii', input='trail_points', type='point', format='point', env=env).strip() # where does trail_points come from?
    c1, c2 = data.splitlines()
    c1 = c1.split('|')
    c2 = c2.split('|')
    points[0] = (float(c1[0]), float(c1[1]))
    points[1] = (float(c2[0]), float(c2[1]))

    # calculate shortest distance between points (replace this with least cost path later)
    gs.read_command("v.net.allpairs", input=data, output=dist_matrix) #data is the map version of the points, right?
    shortest_dist = np.matrix.min(dist_matrix)

    # display the length of this shortest distance


def main():
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"
    elevation = "elev_lid792_1m"
    elev_resampled = "elev_resampled"
    #garden_locations = "" #how do I include this file?
    gs.run_command("g.region", raster=elevation, res=4, flags="a", env=env)
    gs.run_command("r.resamp.stats", input=elevation, output=elev_resampled, env=env)

    run_distance(real_elev=elevation, scanned_elev=elev_resampled, env=env)


if __name__ == "__main__":
    main()
