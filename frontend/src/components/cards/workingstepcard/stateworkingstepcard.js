/*
Filename: stateworkingstepcard.js
Version name: 0.1, 2021-06-18
Short description: Card component for a specific working step

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import axios from "axios";
import {
  Box,
  CardActionArea,
  CardContent,
  Paper,
  Grid,
  Typography,
} from "@material-ui/core";

import EditStateWorkingStepDialog from "../../editdialogs/editworkingstepdialog/editworkingstepdialog";
import ErrorSnackbar from "../../errorsnackbar/errorsnackbar";
import validateWorkingsteps from "../../validateworkingsteps/validateworkingsteps";
import { IP_BACKEND, AUTO_HIDE_DURATION } from ".../../../src/const";

export default function StateWorkingStepCard(props) {
  let allSteps = [];
  let assignedToUnit = 0;
  let name = "";
  let description = "";
  let state = "";
  let task = "";
  let img = "";
  let stepNo = 0;
  let id = 0;
  let color = "";
  let data = new Map();
  let clearDialogOnSave = false;
  let updateStatus = (index, state) => {
    return true;
  };

  const [open, setOpen] = React.useState(false);
  // statemanagment for snackbar
  const [errorState, setErrorState] = React.useState({
    snackbarOpen: false,
    msg: "",
    level: "",
  });
  React.useEffect(() => {
    setTimeout(() => {
      if (errorState.snackbarOpen) {
        setErrorState({
          snackbarOpen: false,
          msg: "",
          level: "",
        });
      }
    }, AUTO_HIDE_DURATION);
  });

  if (props.assignedToUnit) {
    assignedToUnit = props.assignedToUnit;
    data["assignedToUnit"] = assignedToUnit;
  }
  if (props.description) {
    description = props.description;
    data["description"] = description;
  }
  if (props.state) {
    state = props.state;
    data["state"] = state;
  }
  if (props.task) {
    task = props.task;
    data["task"] = task;
  }
  if (props.stepNo) {
    stepNo = props.stepNo;
    data["stepNo"] = stepNo;
  }
  if (props.img) {
    img = props.img;
    data["img"] = img;
  }
  if (props.name) {
    name = props.name;
    data["name"] = name;
  }
  if (props.id) {
    id = props.id;
    data["id"] = id;
  }
  if (props.color) {
    color = props.color;
    data["color"] = color;
  }
  if (props.allSteps) {
    allSteps = props.allSteps;
  }
  if (props.updateStatus) {
    updateStatus = props.updateStatus;
  }
  if (props.clearDialogOnSave) {
    clearDialogOnSave = props.clearDialogOnSave;
  }

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    // set some params and validate other params
    let opNo = 0;
    if (updatedData["task"] === "store") {
      opNo = 210;
    } else if (updatedData["task"] === "unstore") {
      opNo = 213;
    } else if (
      updatedData["task"] === "color" ||
      updatedData["task"] === "package" ||
      updatedData["task"] === "unpackage" ||
      updatedData["task"] === "assemble" ||
      updatedData["task"] === "generic"
    ) {
      opNo = 510;
    } else {
      setErrorState({
        snackbarOpen: true,
        msg: "Internal error: Couldnt assign task a operation number",
        level: "warning",
      });
      return false;
    }

    //update data in Mes
    let payload = {
      name: updatedData["name"],
      description: updatedData["description"],
      task: updatedData["task"],
      color: updatedData["color"],
      stepNo: updatedData["stepNo"],
      operationNo: opNo,
      assignedToUnit: updatedData["assignedToUnit"],
    };
    axios.patch(
      "http://" +
        IP_BACKEND +
        ":8000/api/WorkingStep/" +
        updatedData["id"].toString(),
      payload
    );
    let index = allSteps.findIndex((v) => v.id === updatedData["id"]);
    if (updateStatus(index, updatedData["state"])) {
      return true;
    } else return false;
  };

  const onDelete = (stepToDelete) => {
    let isValid = true;
    let errormsg = "";
    if (allSteps.length !== 0) {
      let newWorkingSteps = allSteps;
      newWorkingSteps.splice(
        newWorkingSteps.findIndex((v) => v.id === stepToDelete["id"]),
        1
      );
      let validator = validateWorkingsteps(newWorkingSteps);
      isValid = validator[0];
      errormsg = validator[1];
    }
    if (isValid) {
      axios.delete(
        "http://" +
          IP_BACKEND +
          ":8000/api/WorkingStep/" +
          stepToDelete["id"].toString()
      );
      return true;
    } else {
      setErrorState({
        snackbarOpen: true,
        msg:
          "Deleting workingstep would make workingplan inexecutable. Reason: " +
          errormsg,
        level: "warning",
      });
      return false;
    }
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
                alt={task}
                width="100px"
                height="100px"
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
        <EditStateWorkingStepDialog
          open={open}
          onClose={handleClose}
          data={data}
          onSave={onSave}
          onDelete={onDelete}
          clearDialogOnSave={clearDialogOnSave}
          title="Edit workingstep"
        />
        <ErrorSnackbar
          level={errorState.level}
          message={errorState.msg}
          isOpen={errorState.snackbarOpen}
        />
      </Paper>
    </Box>
  );
}
