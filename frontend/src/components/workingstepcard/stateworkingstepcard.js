/*
Filename: stateworkingstepcard.js
Version name: 0.1, 2021-05-14
Short description: Card component for a specific working step

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import Box from "@material-ui/core/Box";
import { Grid, Paper } from "@material-ui/core";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardActions from "@material-ui/core/CardActions";
import CardContent from "@material-ui/core/CardContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import Dialog from "@material-ui/core/Dialog";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import { TextField } from "@material-ui/core";

export default function StateWorkingStepCard(props) {
  let assignedToUnit = 0;
  let name = "";
  let description = "";
  let state = "";
  let task = "";
  let img = "";
  let stepNo = 0;

  const [open, setOpen] = React.useState(false);

  if (props.assignedToUnit) {
    assignedToUnit = props.assignedToUnit;
  }
  if (props.description) {
    description = props.description;
  }
  if (props.state) {
    state = props.state;
  }
  if (props.task) {
    task = props.task;
  }
  if (props.stepNo) {
    stepNo = props.stepNo;
  }
  if (props.img) {
    img = props.img;
  }
  if (props.name) {
    name = props.name;
  }

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = (value) => {
    setOpen(false);
  };

  return (
    <Box width={1}>
      <Paper elevation={3}>
        <CardActionArea onClick={handleClickOpen}>
          <Grid
            container
            direction="row"
            alignItems="center"
            justify="flex-start"
            width={1}
          >
            <Grid item>
              <div>&nbsp; &nbsp; &nbsp;</div>
            </Grid>
            <Grid item>
              <img
                src={img}
                alt="Image of task"
                width="100px"
                height="100px"
                alignItems="center"
                margin="10px"
              />
            </Grid>
            <Grid item>
              <div>&nbsp; &nbsp; &nbsp;</div>
            </Grid>
            <Grid item>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  {name}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Task:{" "}
                  </Box>{" "}
                  {task}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Description:{" "}
                  </Box>{" "}
                  {description}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Step number:{" "}
                  </Box>{" "}
                  {stepNo}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    State:{" "}
                  </Box>{" "}
                  {state}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Assigned resource:{" "}
                  </Box>{" "}
                  {assignedToUnit}
                </Typography>
              </CardContent>
            </Grid>
          </Grid>
        </CardActionArea>
        <EditStateWorkingStepDialog open={open} onClose={handleClose} />
      </Paper>
    </Box>
  );
}

function EditStateWorkingStepDialog(props) {
  const { onClose, value, open } = props;

  const handleClose = () => {
    onClose(value);
  };

  const handleListItemClick = (value) => {
    onClose(value);
  };

  return (
    <Dialog
      onClose={handleClose}
      aria-labelledby="simple-dialog-title"
      open={open}
    >
      <DialogTitle id="simple-dialog-title">Edit working step</DialogTitle>
    </Dialog>
  );
}
