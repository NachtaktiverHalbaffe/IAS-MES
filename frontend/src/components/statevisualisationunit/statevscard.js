/*
Filename: statevscard.js
Version name: 0.1, 2021-06-18
Short description: Card component for a state of a specific visualisation unit

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import Box from "@material-ui/core/Box";
import { Grid, Paper } from "@material-ui/core";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardContent from "@material-ui/core/CardContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import Dialog from "@material-ui/core/Dialog";
import Button from "@material-ui/core/Button";
import Typography from "@material-ui/core/Typography";
import { TextField } from "@material-ui/core";

export default function StateVSCard(props) {
  let boundToRessource = "";
  let state = "";
  let ipadress = "";
  let baseLevelHeight = "";
  let task = "";
  let img = "";
  let data = new Map();

  const [open, setOpen] = React.useState(false);

  if (props.boundToRessource) {
    boundToRessource = props.boundToRessource;
    data["boundToRessource"] = boundToRessource;
  }
  if (props.ipadress) {
    ipadress = props.ipadress;
    data["ipadress"] = ipadress;
  }
  if (props.state) {
    state = props.state;
    data["state"] = state;
  }
  if (props.task) {
    task = props.task;
    data["task"] = task;
  }
  if (props.baseLevelHeight) {
    baseLevelHeight = props.baseLevelHeight;
    data["baseLevelHeight"] = baseLevelHeight;
  }
  if (props.img) {
    img = props.img;
    data["img"] = img;
  }

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = (data) => {
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
                alt="Image of resource"
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
                  {"Visualisation Unit " + boundToRessource}
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
                    IP-Adress:{" "}
                  </Box>{" "}
                  {ipadress}
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
                    Baselevel Height:{" "}
                  </Box>{" "}
                  {baseLevelHeight.toString()}
                </Typography>
              </CardContent>
            </Grid>
          </Grid>
        </CardActionArea>
        <EditStateVSDialog open={open} onClose={handleClose} data={data} />
      </Paper>
    </Box>
  );
}

function EditStateVSDialog(props) {
  const { onClose, value, open, data } = props;

  const handleClose = () => {
    onClose(data);
  };

  return (
    <Dialog
      onClose={handleClose}
      aria-labelledby="simple-dialog-title"
      open={open}
    >
      <DialogTitle id="simple-dialog-title">
        Edit state of visualisation unit
      </DialogTitle>
    </Dialog>
  );
}
