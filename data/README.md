# Overview

Each subdirectory contains correction factor calculations for a set of drifter data, ocean model outputs, and atmosphere model outputs. Two types of correction factors where computed:

1. Ocean correction factor $`\gamma`$

Solves for $`\gamma`$ in

$`u_{drifter} = \gamma u_{ocean}`$

2. Wind correction factor $`\alpha`$

Solves for $`\alpha`$ in

$`u_{drifter} = u_{ocean} + \alpha u_{atmos}`$

where $`u_{drifter}`$, $`u_{ocean}`$ and $`u_{atmos}`$ are the current vectors for the drifter, ocean and winds respectively.

Drifter positions and velocity resampled to an hourly frequency are available in each output file. Ocean currents and winds interpolated to the drifter positions are also provided.

Output files are per individual drifter where each drifter has a unique identifier (buoyid).