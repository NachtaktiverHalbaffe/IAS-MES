/*
Filename: editworkingplandialog.js
Version name: 0.1, 2021-06-27
Short description: Dialog to edit/create a workingstep

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { Button, Dialog, DialogTitle, ListItem } from "@material-ui/core";

import EditTextBox from "../../edittextbox/edittextbox";
import { AUTO_HIDE_DURATION } from "../../../const";

export default function EditStateWorkingPlanDialog(props) {
  const { onClose, onSave, onDelete, open, data, title } = props;
  const [state, setState] = React.useState(data);
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

  const handleClose = () => {
    onClose();
  };

  const handleSave = () => {
    if (state["name"].length > 30) {
      setErrorState({
        snackbarOpen: true,
        msg: "Name too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    if (state["description"] !== "") {
      if (state["description"].length > 200) {
        setErrorState({
          snackbarOpen: true,
          msg: "Description too long. Max length: 30",
          level: "warning",
        });
        return false;
      }
    }
    if (isNaN(state["workingPlanNo"]) || state["workingPlanNo"] < 1) {
      setErrorState({
        snackbarOpen: true,
        msg: "Workingplan isnt a positive number",
        level: "warning",
      });
      return false;
    }
    if (onSave(state)) {
      handleClose();
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

  return (
    <Dialog
      onClose={handleClose}
      aria-labelledby="simple-dialog-title"
      open={open}
    >
      <DialogTitle id="simple-dialog-title">{title}</DialogTitle>
      <EditTextBox
        label="Name"
        mapKey="name"
        initialValue={data["name"]}
        helperText="Name of the workingplan"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Description"
        mapKey="description"
        initialValue={data["description"]}
        helperText="Description of the workingplan(optional)"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Workingplan number"
        mapKey="workingPlanNo"
        initialValue={data["workingPlanNo"]}
        helperText="Number of the workingplan. Identifies the workingplan"
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
    </Dialog>
  );
}
