/*
Filename: editorderdialog.js
Version name: 0.1, 2021-06-27
Short description: Dialog to edit/create a order

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { Button, Dialog, DialogTitle, ListItem } from "@material-ui/core";

import EditTextBox from "../../edittextbox/edittextbox";
import ErrorSnackbar from "../../errorsnackbar/errorsnackbar";
import { AUTO_HIDE_DURATION } from "../../../../src/const";

export default function EditStateOrderDialog(props) {
  const { onClose, onSave, open, data, title } = props;
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
    //validate data
    if (isNaN(state["orderNo"]) || state["orderNo"] < 1) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid ordernumber. Must be a positive number and not 0",
        level: "warning",
      });
      return false;
    }
    if (isNaN(state["orderPos"]) || state["orderpos"] < 1) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid order position. Must be a positive number and not 0",
        level: "warning",
      });
      return false;
    }
    if (state["name"].length > 30) {
      setErrorState({
        snackbarOpen: true,
        msg: "Name too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    if (state["description"].length > 200) {
      setErrorState({
        snackbarOpen: true,
        msg: "Description too long. Max length: 200",
        level: "warning",
      });
      return false;
    }
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
      <DialogTitle id="simple-dialog-title">{title}</DialogTitle>
      <EditTextBox
        label="Name"
        mapKey="name"
        initialValue={data["name"]}
        helperText="Name of the order"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Description"
        mapKey="description"
        initialValue={data["description"]}
        helperText="Description of the order (optional)"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Order number"
        mapKey="orderNo"
        initialValue={data["orderNo"]}
        helperText="Order number of the order"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Order position"
        mapKey="orderPos"
        initialValue={data["orderPos"]}
        helperText="Position of an order within the order itself if an order contains multiple orders"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Costumer"
        mapKey="costumer"
        initialValue={data["costumer"]}
        helperText="Name of the costumer who assigned the order(optional). Only change if new costumer is already created as an costumer"
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
      <ErrorSnackbar level={level} message={msg} isOpen={snackbarOpen} />
    </Dialog>
  );
}
