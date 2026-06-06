This Python script is intended to be executed via command-line. Moon orbit data obtained from JPL (https://ssd.jpl.nasa.gov/sats/elem/sep.html), code partially written by Claude AI, fact-checked and corrected by Nrco0e.

This script plots the 3D orbits of a planet's major and irregular moons by querying JPL Horizons (astroquery) for their positions over time, and then plotting them in 3D space.

For each moon, one full orbit is shown, constructed with 500 points. The timestep is adjusted according to their average orbital period listed by JPL (see above link).
