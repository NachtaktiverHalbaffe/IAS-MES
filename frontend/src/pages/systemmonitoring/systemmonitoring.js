import React from 'react';
import Grid from '@material-ui/core/Grid';

import StatePLCCard from '../../components/stateplccard/stateplccard';

import branch from '../../assets/branch.png'

export default function SystemMonitoring(){

    return(
        <div>
            <Grid container spacing={1} direction="column">
                <Grid item  >
                  <StatePLCCard name="Branch 2" mode="auto" image= {branch} state="idle" resourceId= "2" />
                </Grid>
            </Grid>
        </div>
    );
};