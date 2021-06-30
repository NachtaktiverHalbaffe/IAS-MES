import React from "react";
import { Button, Dialog, DialogTitle, ListItem } from "@material-ui/core";

import EditTextBox from "../edittextbox/edittextbox";

export default function EditStateWorkingStepDialog(props) {
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
