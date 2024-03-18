#!/usr/bin/env python3

##############################################################################
# AUTHOR(S):    Qasim Adegbite
##############################################################################

# terrain_generator.py

#!/usr/bin/env python3

import os
import numpy as np
import grass.script as gs


def generate_terrain(rows, cols, env):
    # Generate synthetic elevation data
    elevation = np.random.rand(rows, cols) * 1000
    np.savetxt('elevation.txt', elevation, fmt='%f')

    # Import elevation data into GRASS GIS
    gs.run_command("r.in.xyz", input="elevation.txt", output="synthetic_elevation", separator="comma", flags="o", env=env)

    # Compute slope using GRASS GIS
    gs.run_command("r.slope.aspect", elevation="synthetic_elevation", slope="synthetic_slope", env=env)


def main():
    # Set up GRASS GIS environment
    env = os.environ.copy()
    env["GRASS_OVERWRITE"] = "1"

    # Set the number of rows and columns for synthetic terrain
    rows = 100
    cols = 100

    # Generate synthetic terrain data
    generate_terrain(rows, cols, env)


if __name__ == "__main__":
    main()
