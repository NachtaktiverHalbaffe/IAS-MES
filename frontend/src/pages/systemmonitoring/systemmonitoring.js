/*
Filename: systemmonitoring.js
Version name: 0.1, 2021-06-18
Short description: Page with all components to show system state

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { Grid, Typography } from "@material-ui/core";

import ListStates from "./liststates";
import ListVSStates from "./listvsstates";
import ListStateWorkingSteps from "./liststateworkingsteps";
import ListStateWorkingPieces from "./liststatesworkingpieces";

export default function SystemMonitoring() {
  return (
    <Grid container direction="row" justify="space-around" alignItems="stretch">
      <Grid item xs={8}>
        <Grid
          container
          direction="column"
          justify="flex-start"
          alignItems="center"
        >
          <Grid item xs container direction="column" spacing={2}>
            <Typography gutterBottom variant="h5" component={"span"}>
              States of the resources
            </Typography>
            <ListStates />
          </Grid>

          <Grid
            item
            xs
            container
            direction="column"
            spacing={2}
            alignItems="center"
          >
            <div>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</div>
            <Typography gutterBottom variant="h5" component={"span"}>
              States of the visualisation units
            </Typography>
            <ListVSStates />
          </Grid>
          <Grid item xs>
            <div>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp;</div>
            <Typography gutterBottom variant="h5" component={"span"}>
              States of the workingpieces
            </Typography>
            <ListStateWorkingPieces />
          </Grid>
        </Grid>
      </Grid>
      <Grid item xs={3}>
        <Grid item xs container direction="column" spacing={2}>
          <Typography gutterBottom variant="h5" component={"span"}>
            Current Order
          </Typography>
          <ListStateWorkingSteps />
        </Grid>
      </Grid>
    </Grid>
  );
}
