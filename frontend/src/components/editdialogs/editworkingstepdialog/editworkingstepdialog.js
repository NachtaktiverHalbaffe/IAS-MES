/*
Filename: editworkingstepdialog.js
Version name: 0.1, 2021-06-22
Short description: Card component for a specific working step

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import {
  Box,
  Button,
  Grid,
  Dialog,
  DialogTitle,
  ListItem,
} from "@material-ui/core";

import EditTextBox from "../../edittextbox/edittextbox";
import EditChoiceBox from "../../edittextbox/editchoicebox";
import ErrorSnackbar from "../../errorsnackbar/errorsnackbar";
import { AUTO_HIDE_DURATION, DEFINED_TASKS } from "../../../../src/const";
import { ChromePicker } from "react-color";

export default function EditStateWorkingStepDialog(props) {
  const { onClose, onSave, onDelete, open, data, title } = props;
  const [state, setState] = React.useState(data);
  const [color, setColor] = React.useState(data["color"]);

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

  const handleClose = () => {
    onClose();
  };

  const handleSave = () => {
    // validate data
    if (!DEFINED_TASKS.includes(state["task"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Unkown tasks. Defined tasks: " + DEFINED_TASKS.toString(),
        level: "warning",
      });
      return false;
    }
    //validate stepNo. It has to be a multiple of 10
    if (state["stepNo"] % 10 !== 0) {
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
    if (!/^#[0-9A-F]{6}$/i.test(state["color"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Color is not formatted as a hex color. Format: #0dccff",
        level: "warning",
      });
      return false;
    }
    // validate if name is shorter than 30 characters
    if (state["name"].length > 30) {
      setErrorState({
        snackbarOpen: true,
        msg: "Name is too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    // validate if description is shorter than 200 character
    if (state["description"] > 200) {
      setErrorState({
        snackbarOpen: true,
        msg: "Description is too long.Max length: 200",
        level: "warning",
      });
      return false;
    }
    if (
      isNaN(state["assignedToUnit"]) ||
      state["assignedToUnit"] < 1 ||
      state["assignedToUnit"] > 6
    ) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid resourceId of assigned unit. Value must be between 1-6",
        level: "warning",
      });
      return false;
    }

    if (onSave(state)) {
      setErrorState({
        snackbarOpen: true,
        msg: "Sucessfully added workingstep",
        level: "success",
      });
      handleClose();
      return true;
    }
  };

  const handleDelete = () => {
    if (onDelete(state)) {
      handleClose();
      return true;
    }
  };

  const onEdit = (key, value) => {
    let newState = state;
    newState[key] = value;
    setState(newState);
  };

  const onColorEdit = (value) => {
    let newState = state;
    newState["color"] = value.hex;
    setState(newState);
    setColor(value.hex);
  };

  return (
    <Box>
      {" "}
      <ErrorSnackbar
        level={errorState.level}
        message={errorState.msg}
        isOpen={errorState.snackbarOpen}
      />
      <Dialog
        onClose={handleClose}
        aria-labelledby="simple-dialog-title"
        open={open}
      >
        <DialogTitle id="simple-dialog-title">{title}</DialogTitle>
        <Grid container direction="column" justify="center" alignItems="center">
          <EditTextBox
            label="Name"
            mapKey="name"
            initialValue={data["name"]}
            helperText="Name of the workingstep"
            onEdit={onEdit}
          />
          <EditChoiceBox
            label="Task"
            mapKey="task"
            initialValue={data["task"]}
            helperText="Task which gets executed on the resource"
            onEdit={onEdit}
            choices={DEFINED_TASKS}
          />
          <Grid item>
            <ChromePicker color={color} onChangeComplete={onColorEdit} />
          </Grid>
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
            <div>&nbsp; &nbsp; &nbsp;</div>
            <Button
              justify="flex-end"
              variant="outlined"
              color="primary"
              href="#outlined-buttons"
              onClick={handleDelete}
            >
              Delete
            </Button>
          </ListItem>
        </Grid>
      </Dialog>
    </Box>
  );
}
