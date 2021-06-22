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
  Button,
  CardActionArea,
  CardContent,
  Dialog,
  DialogTitle,
  Grid,
  ListItem,
  Paper,
  Typography,
} from "@material-ui/core";

import EditTextBox from "../edittextbox/edittextbox";
import ErrorSnackbar from "../errorsnackbar/errorsnackbar";
import { IP_BACKEND, DEFINED_TASKS, AUTO_HIDE_DURATION } from "../../const";

export default function StateWorkingStepCard(props) {
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

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    // set some params and validate other params
    let opNo = 0;
    //task name valid? (defined in DEFINED_TASKS and model in backend)
    if (!DEFINED_TASKS.includes(updatedData["task"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Unkown tasks. Defined tasks: " + DEFINED_TASKS.toString(),
        level: "warning",
      });
      return false;
    }
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
        msg: "Internal error",
        level: "warning",
      });
      return false;
    }
    //validate stepNo. It has to be a multiple of 10
    if (updatedData["stepNo"] % 10 !== 0) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid step number. Step number must be a multiple of 10",
        level: "warning",
      });
      return false;
    }
    // validate if color os vaslid hexcolor
    //expression !/^#[0-9A-F]{6}$/i:
    // ^# check if first char is #
    // [0-9A-F]{6} check if next 6 characters are 0-9 or a-f
    if (!/^#[0-9A-F]{6}$/i.test(updatedData["color"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Color is not formatted as a hex color. Format: #0dccff",
        level: "warning",
      });
      return false;
    }
    // validate if name is shorter than 30 characters
    if (updatedData["name"].length > 30) {
      setErrorState({
        snackbarOpen: true,
        msg: "Name is too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    // validate if description is shorter than 200 character
    if (updatedData["description"] > 200) {
      setErrorState({
        snackbarOpen: true,
        msg: "Description is too long.Max length: 200",
        level: "warning",
      });
      return false;
    }
    if (
      isNaN(updatedData["assignedToUnit"]) ||
      updatedData["assignedToUnit"] < 1 ||
      updatedData["assignedToUnit"] > 6
    ) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid resourceId of assigned unit. Value must be between 1-6",
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
    setErrorState({
      snackbarOpen: true,
      msg: "Sucessfully updated workingstep",
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
        <EditStateWorkingStepDialog
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

function EditStateWorkingStepDialog(props) {
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
      <DialogTitle id="simple-dialog-title">Edit workingstep</DialogTitle>
      <EditTextBox
        label="Name"
        mapKey="name"
        initialValue={data["name"]}
        helperText="Name of the workingstep"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Task"
        mapKey="task"
        initialValue={data["task"]}
        helperText="Task which gets executed on the resource"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Description"
        mapKey="description"
        initialValue={data["description"]}
        helperText="Description of the workingstep(optional)"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Step number"
        mapKey="stepNo"
        initialValue={data["stepNo"]}
        helperText="Step number of the workingstep. Workingsteps gets executed in ascending order"
        onEdit={onEdit}
      />
      <EditTextBox
        label="State"
        mapKey="state"
        initialValue={data["state"]}
        helperText="If workingstep is pending or finished"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Assigned resource"
        mapKey="assignedToUnit"
        initialValue={data["assignedToUnit"]}
        helperText="Id of assigned resource and mounted visualisation unit of the workingstep"
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
