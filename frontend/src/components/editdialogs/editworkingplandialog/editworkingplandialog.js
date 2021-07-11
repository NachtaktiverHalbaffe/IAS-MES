/*
Filename: editworkingplandialog.js
Version name: 1.0, 2021-07-10
Short description: Dialog to edit/create a workingplan

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import {Button, Dialog, DialogTitle, ListItem} from "@material-ui/core";

import EditTextBox from "../../edittextbox/edittextbox";
import {AUTO_HIDE_DURATION} from "../../../const";

export default function EditStateWorkingPlanDialog(props) {
    const {
        onClose,
        onSave,
        onDelete,
        open,
        data,
        title
    } = props;
    const [state, setState] = React.useState(data);

    // statemanagment for snackbar
    const [errorState, setErrorState] = React.useState({snackbarOpen: false, msg: "", level: ""});
    // close snackbar after AUTO_HIDE_DURATION exceeded
    React.useEffect(() => {
        setTimeout(() => {
            if (errorState.snackbarOpen) {
                setErrorState({snackbarOpen: false, msg: "", level: ""});
            }
        }, AUTO_HIDE_DURATION);
    });

    // callback when the save button is pressed
    const handleSave = () => {
        if (state["name"].length > 30) {
            setErrorState({snackbarOpen: true, msg: "Name too long. Max length: 30", level: "warning"});
            return false;
        }
        // validate if name is given because name is required argument
        if (state["name"] === "") {
            setErrorState({snackbarOpen: true, msg: "Name is required", level: "error"});
            return false;
        }
        if (state["description"] !== "") {
            if (state["description"].length > 200) {
                setErrorState({snackbarOpen: true, msg: "Description too long. Max length: 30", level: "warning"});
                return false;
            }
        }
        if (isNaN(state["workingPlanNo"]) || state["workingPlanNo"] < 1) {
            setErrorState({snackbarOpen: true, msg: "Workingplan isnt a positive number", level: "warning"});
            return false;
        }
        if (onSave(state)) {
            onClose();
        }
    };

    // callback when delete button is pressed
    const handleDelete = () => {
        if (onDelete(state)) {
            onClose();
            return true;
        }
    };

    // update state of dialog when a value gets changed
    const onEdit = (key, value) => {
        let newState = state;
        newState[key] = value;
        setState(newState);
    };

    return (
        <Dialog onClose={
                () => {
                    onClose();
                }
            }
            aria-labelledby="simple-dialog-title"
            open={open}>
            <DialogTitle id="simple-dialog-title">
                {title}</DialogTitle>
            <EditTextBox label="Name" mapKey="name"
                initialValue={
                    data["name"]
                }
                helperText="Name of the workingplan"
                onEdit={onEdit}/>
            <EditTextBox label="Description" mapKey="description"
                initialValue={
                    data["description"]
                }
                helperText="Optional: Description of the workingplan"
                onEdit={onEdit}/>
            <EditTextBox label="Workingplan number" mapKey="workingPlanNo"
                initialValue={
                    data["workingPlanNo"]
                }
                helperText="Number of the workingplan. Identifies the workingplan"
                onEdit={onEdit}/>
            <ListItem justify="flex-end">
                <Button justify="flex-end" variant="outlined" color="primary"
                    onClick={handleSave}>
                    Save
                </Button>
                <div>&nbsp; &nbsp; &nbsp;</div>
                <Button justify="flex-end" variant="outlined" color="primary"
                    onClick={handleDelete}>
                    Delete
                </Button>
            </ListItem>
        </Dialog>
    );
}
