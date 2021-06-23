/*
Filename: systemmonitoring.js
Version name: 0.1, 2021-06-18
Short description: Page with all components to show system state

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { Box } from "@material-ui/core";
import Grid from "@material-ui/core/Grid";
import { Typography } from "@material-ui/core";

import ListStates from "./liststates";
import ListVSStates from "./listvsstates";
import ListStateWorkingSteps from "./liststateworkingsteps";

export default function SystemMonitoring() {
  return (
    <Grid container direction="row" justify="space-around" alignItems="stretch">
      <Grid item xs={8}>
        <Grid
          container
          direction="column"
          justify="flex-start"
          alignItems="Center"
        >
          <Grid
            item
            xs
            container
            direction="column"
            spacing={2}
            alignItems="center"
          >
            <Typography gutterBottom variant="h5" component="h2">
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
            <Typography gutterBottom variant="h5" component="h2">
              States of the visualisation units
            </Typography>
            <ListVSStates />
          </Grid>
        </Grid>
      </Grid>
      <Grid item xs={3} alignItems="center">
        <Grid
          item
          xs
          container
          direction="column"
          spacing={2}
          alignItems="center"
        >
          <Typography gutterBottom variant="h5" component="h2">
            Current Order
          </Typography>
          <ListStateWorkingSteps />
        </Grid>
      </Grid>
    </Grid>
  );
}
