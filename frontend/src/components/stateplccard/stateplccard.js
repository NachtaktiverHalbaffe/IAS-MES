import React from 'react';
import Box  from '@material-ui/core/Box';
import { Grid, Paper } from '@material-ui/core';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import DialogTitle from '@material-ui/core/DialogTitle';
import Dialog from '@material-ui/core/Dialog';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';
import { TextField } from '@material-ui/core';


export default function StatePLCCard(props){
    
    let name = "";
    let mode ="";
    let state = "";
    let image ="";
    let resourceId = "";

    const [open, setOpen] = React.useState(false);

    if(props.name){
        name =props.name;
    } if(props.image){
        image= props.image;
    } if(props.state){
        state= props.state;
    } if(props.mode){
        mode= props.mode;
    } if(props.resourceId){
        resourceId= props.resourceId;
    } 

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = (value) => {
    setOpen(false);

  };

  
  return (
    <Box width= {1}>
      <Paper elevation={3}>
        <CardActionArea onClick={handleClickOpen}>
        <Grid container direction="row" alignItems="center"  justify="flex-start" width ="1000px">
          <Grid item >
            <div>
              &nbsp;
              &nbsp;
              &nbsp;
            </div>
          </Grid>
          <Grid item>
              <img 
                src={image} 
                alt="Image of resource"
                width= "100px"
                height="100px"
                alignItems = "center"
                margin = "10px"
                />
          </Grid>
          <Grid item >
            <div>
              &nbsp;
              &nbsp;
              &nbsp;
            </div>
          </Grid>
          <Grid item>
            <CardContent>
            <Typography gutterBottom variant="h5" component="h2">
              {name}
            </Typography>
            <Typography variant="body1" color="textSecondary" component='div'>
              <Box fontWeight='fontWeightBold' display='inline'>State: </Box> {state}
            </Typography>
            <Typography variant="body1" color="textSecondary" component='div'>
              <Box fontWeight='fontWeightBold' display='inline'>ResourceId: </Box> {resourceId}
            </Typography>
            <Typography variant="body1" color="textSecondary" component='div'>
              <Box fontWeight='fontWeightBold' display='inline'>Mode: </Box> {mode}
            </Typography>
            </CardContent>
          </Grid>
        </Grid>
        </CardActionArea>
         <EditStatePLCDialog open={open} onClose={handleClose} />
      </Paper>
    </Box>
  );
}

function EditStatePLCDialog(props) {
  const { onClose, value,open } = props;

  let name = "";
  let mode ="";
  let state = "";
  let image ="";
  let resourceId = "";
  let task = "";

    if(props.name){
        name =props.name;
    } if(props.image){
        image= props.image;
    } if(props.state){
        state= props.state;
    } if(props.mode){
        mode= props.mode;
    } if(props.resourceId){
        resourceId= props.resourceId;
    } if(props.task){
        task= props.task;
    } 

  const handleClose = () => {
     onClose(value);
  };

  const handleListItemClick = (value) => {
     onClose(value);
  };

  return (
    <Dialog onClose={handleClose} aria-labelledby="simple-dialog-title" open={open}>
      <DialogTitle id="simple-dialog-title">Edit State of Resource</DialogTitle>
    </Dialog>
  );
}

