/*
Filename: statevscard.js
Version name: 0.1, 2021-06-18
Short description: Card component for a state of a specific visualisation unit

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import axios from "axios";
import {
  Box,
  Button,
  Grid,
  CardActionArea,
  CardContent,
  DialogTitle,
  Dialog,
  ListItem,
  Paper,
  Typography,
} from "@material-ui/core";

import EditTextBox from "../edittextbox/edittextbox";
import ErrorSnackbar from "../errorsnackbar/errorsnackbar";
import {
  IP_BACKEND,
  AUTO_HIDE_DURATION,
  DEFINED_VS_TASKS,
  DEFINED_VS_STATES,
} from "../../const";

export default function StateVSCard(props) {
  let boundToRessource = "";
  let state = "";
  let ipadress = "";
  let baseLevelHeight = "";
  let task = "";
  let img = "";
  let data = new Map();

  const [open, setOpen] = React.useState(false);
  // statemanagment for snackbar
  const [errorState, setErrorState] = React.useState({
    snackbarOpen: false,
    msg: "",
    level: "",
  });
  const { level, msg, snackbarOpen } = errorState;
  React.useEffect(() => {
    setTimeout(() => {
      if (snackbarOpen) {
        setErrorState({
          snackbarOpen: false,
          msg: "",
          level: "",
        });
      }
    }, AUTO_HIDE_DURATION);
  });

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

  const handleClose = () => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    // validate data
    if (
      isNaN(updatedData["boundToRessource"]) ||
      updatedData["boundToRessource"] < 2 ||
      updatedData["boundToRessource"] > 6
    ) {
      setErrorState({
        snackbarOpen: true,
        msg:
          "Invalid resourceId of resource where unit is mounted to. Must be an integer between 2-6",
        level: "warning",
      });
      return false;
    }
    if (
      isNaN(updatedData["baseLevelHeight"]) ||
      updatedData["baseLevelHeight"] < 0.0
    ) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid baselevel height. Must be an positive float",
        level: "warning",
      });
      return false;
    }
    let ipAdressSplit = updatedData["ipadress"].split(".");
    if (
      ipAdressSplit.length !== 4 ||
      isNaN(ipAdressSplit[0]) ||
      isNaN(ipAdressSplit[1]) ||
      isNaN(ipAdressSplit[2]) ||
      isNaN(ipAdressSplit[3]) ||
      ipAdressSplit[0].length > 3 ||
      ipAdressSplit[1].length > 3 ||
      ipAdressSplit[2].length > 3 ||
      ipAdressSplit[3].length > 3
    ) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid id adress. Format(ipv4): e.g. 129.69.102.129 ",
        level: "warning",
      });
      return false;
    }
    if (!DEFINED_VS_TASKS.includes(updatedData["task"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Unkown tasks. Defined tasks: " + DEFINED_VS_TASKS.toString(),
        level: "warning",
      });
      return false;
    }
    if (!DEFINED_VS_STATES.includes(updatedData["state"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Unkown state. Defined states: " + DEFINED_VS_STATES.toString(),
        level: "warning",
      });
      return false;
    }
    //update data in Mes
    axios.patch(
      "http://" +
        IP_BACKEND +
        ":8000/api/StateVisualisationUnit/" +
        updatedData["boundToRessource"].toString(),
      {
        boundToRessource: updatedData["boundToRessource"],
        baseLevelHeight: updatedData["baseLevelHeight"],
        assignedTask: updatedData["task"],
        ipAdress: updatedData["ipadress"],
        state: updatedData["state"],
      }
    );
    setErrorState({
      snackbarOpen: true,
      msg: "Sucessfully updated state of visualisation unit",
      level: "success",
    });
    return true;
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
        <EditStateVSDialog
          open={open}
          onClose={handleClose}
          data={data}
          onSave={onSave}
        />
      </Paper>
      <ErrorSnackbar level={level} message={msg} isOpen={snackbarOpen} />
    </Box>
  );
}

function EditStateVSDialog(props) {
  const { onClose, onSave, open, data } = props;
  const [state, setState] = React.useState(data);

  const handleClose = () => {
    onClose();
  };

  const handleSave = () => {
    if (onSave(state)) {
      handleClose();
    }
  };

  const onEdit = (key, value) => {
    let newState = state;
    newState[key] = value;
    setState(newState);
  };

  return (
    <Dialog
      onClose={handleClose}
      aria-labelledby="simple-dialog-title"
      open={open}
    >
      <DialogTitle id="simple-dialog-title">
        {"Edit state of visualisation unit " +
          data["boundToRessource"].toString()}
      </DialogTitle>
      <EditTextBox
        label="State"
        mapKey="state"
        initialValue={data["state"]}
        helperText="State of the visualisation unit. Only change if you know what are you doing!"
        onEdit={onEdit}
      />
      <EditTextBox
        label="IP-Adress"
        mapKey="ipAdress"
        initialValue={data["ipadress"]}
        helperText="IP-Adress of the visualisation unit. Only change if you know what are you doing! "
        onEdit={onEdit}
      />
      <EditTextBox
        label="Task"
        mapKey="task"
        initialValue={data["task"]}
        helperText="Current visualisation task which is assigned to the unit. Only change if you know what are you doing!"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Baselevel height"
        mapKey="baseLevelHeight"
        initialValue={data["baseLevelHeight"]}
        helperText="Baselevel of the ultrasonic sensor. Gets calibrated on startup of the unit. Only change if you know what are you doing!"
        onEdit={onEdit}
      />
      <ListItem justify="flex-end">
        <Button
          justify="flex-end"
          variant="outlined"
          color="primary"
          href="#outlined-buttons"
          onClick={handleSave}
        >
          Save
        </Button>
      </ListItem>
    </Dialog>
  );
}
