import React from 'react';
import { Box } from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import { Typography } from '@material-ui/core';

import ListStates from '../../components/stateplccard/liststates';
import ListVSStates from '../../components/statevisualisationunit/listvsstates';

export default function SystemMonitoring(){

    return(

            <Grid container  
                direction="column"
                justify="flex-start"
                alignItems="stretch">
                <Grid item >
                    <Typography gutterBottom variant="h5" component="h2">
                        States of the resources
                    </Typography>
                </Grid>
                <Grid item>
                    <ListStates/>   
                </Grid>
                <Grid item >
                    <div>
                    &nbsp;
                    &nbsp;
                    &nbsp;
                    &nbsp;
                    &nbsp;
                    </div>
                </Grid>
                <Grid item >
                    <Typography gutterBottom variant="h5" component="h2">
                        States of the visualisation units
                    </Typography>
                </Grid>
                <Grid item>
                    <ListVSStates/>
                </Grid>
            </Grid> 
  
    );
};