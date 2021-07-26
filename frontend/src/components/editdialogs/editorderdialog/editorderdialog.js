/*
Filename: editorderdialog.js
Version name: 1.0, 2021-07-10
Short description: Dialog to edit/create a order

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, {useEffect, useLayoutEffect} from "react";
import axios from "axios";
import {Button, Dialog, DialogTitle, ListItem} from "@material-ui/core";

import EditTextBox from "../../edittextbox/edittextbox";
import EditChoiceBox from "../../edittextbox/editchoicebox";
import ErrorSnackbar from "../../errorsnackbar/errorsnackbar";
import {IP_BACKEND, AUTO_HIDE_DURATION} from "../../../../src/const";
import validateWorkingPiece from "../../validateWorkingPiece/validateWorkingPiece";

export default function EditStateOrderDialog(props) {
    const {
        onClose,
        onSave,
        onDelete,
        open,
        data,
        title
    } = props;
    const [state, setState] = React.useState(data);
    const [workingPieces, setWorkingPieces] = React.useState([]);

    // statemanagment for snackbar
    const [errorState, setErrorState] = React.useState({snackbarOpen: false, msg: "", level: ""});
    const {level, msg, snackbarOpen} = errorState;
    // close snackbar after AUTO_HIDE_DURATION exceeded
    React.useEffect(() => {
        setTimeout(() => {
            if (snackbarOpen) {
                setErrorState({snackbarOpen: false, msg: "", level: ""});
            }
        }, AUTO_HIDE_DURATION);
    });

    // poll data from backend
    useEffect(() => {
        const pollingTime = 2; // interval for polling in seconds

        const interval = setInterval(async () => {
            getDataFromMes();
        }, pollingTime * 1000);
        return() => clearInterval(interval);
    });

    useLayoutEffect(() => {
        getDataFromMes();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    // callback when dialog is closed
    const handleClose = () => {
        onClose();
    };

    // callback when delete button is pressed
    const handleDelete = () => {
        if (onDelete(state)) {
            handleClose();
            return true;
        }
    };

    // callback when the save button is pressed
    const handleSave = () => {
        // validate data
        // name too long
        if (state["name"].length > 30) {
            setErrorState({snackbarOpen: true, msg: "Name too long. Max length: 30", level: "error"});
            return false;
        }
        // name is required
        if (state["name"] === "") {
            setErrorState({snackbarOpen: true, msg: "Name is required", level: "error"});
            return false;
        }
        // ordernumber not a number or less than 1
        if (isNaN(state["orderNo"]) || state["orderNo"] < 1) {
            setErrorState({snackbarOpen: true, msg: "Invalid ordernumber. Must be a positive number and not 0", level: "error"});
            return false;
        }
        if (isNaN(state["orderPos"]) || state["orderpos"] < 1) {
            setErrorState({snackbarOpen: true, msg: "Invalid order position. Must be a positive number and not 0", level: "error"});
            return false;
        }
        if (state["description"] !== undefined) {
            if (state["description"].length > 200) {
                setErrorState({snackbarOpen: true, msg: "Description too long. Max length: 200", level: "error"});
                return false;
            }
        }
        if (state["customer"] !== undefined) {
            let name = state["customer"].split(" ");
            if (name.length !== 2 && state["customer"].length !== 0) {
                setErrorState({snackbarOpen: true, msg: "Invalid name. Please enter a fristname and lastname e.g. John Doe", level: "error"});
                return false;
            } else if (state["customerNo"] === 0 && state["customer"].length !== 0) {
                setErrorState({snackbarOpen: true, msg: "Customer doesnt exist. Make sure to type the name wright", level: "error"});
                return false;
            }
        }
        if (onSave(state)) {
            handleClose();
        }
    };

    // update state of dialog when a value gets changed
    const onEdit = async (key, value) => {
        let newState = state;
        // check if customer exists and then assign customerNo
        if (key === "customer") {
            let name = value.split(" ");
            if (name.length === 2) {
                axios.get("http://" + IP_BACKEND + ":8000/api/Customer/byName/" + name[0] + "/" + name[1]).then(async (res) => {
                    if (res.data.length === 1) {
                        if (!isNaN(res.data[0]["customerNo"])) {
                            newState["customerNo"] = res.data[0]["customerNo"];
                        }
                    } else {
                        newState["customerNo"] = 0;
                    }
                });
            } else {
                newState["customerNo"] = "";
            }
        } else if (key === "assignedWorkingPiece") { // validate if workingpiece has right state
            axios.get("http://" + IP_BACKEND + ":8000/api/StateWorkingPiece/" + value.toString()).then((res) => {
                const validator = validateWorkingPiece(data["allSteps"], res.data);
                if (validator[0]) {
                    newState[key] = value;
                    setState(newState);
                } else {
                    setErrorState({snackbarOpen: true, msg: validator[1], level: "error"});
                }
            });
        } else {
            newState[key] = value;
            setState(newState);
        }
    };

    // get data from backend
    function getDataFromMes() {
        axios.get("http://" + IP_BACKEND + ":8000/api/StateWorkingPiece/").then((res) => {
            let workingPieceIds = [];
            for (let i = 0; i < res.data.length; i++) {
                workingPieceIds.push(res.data[i].id);
            }
            setWorkingPieces(workingPieceIds);
        });
    }

    return (
        <Dialog onClose={handleClose}
            aria-labelledby="simple-dialog-title"
            open={open}>
            <DialogTitle id="simple-dialog-title">
                {title}</DialogTitle>
            <EditTextBox label="Name" mapKey="name"
                initialValue={
                    data["name"]
                }
                helperText="Name of the order"
                onEdit={onEdit}/>
            <EditTextBox label="Description" mapKey="description"
                initialValue={
                    data["description"]
                }
                helperText="Optional: Description of the order"
                onEdit={onEdit}/>
            <EditTextBox label="Order number" mapKey="orderNo"
                initialValue={
                    data["orderNo"]
                }
                helperText="Order number of the order"
                onEdit={onEdit}/>
            <EditTextBox label="Order position" mapKey="orderPos"
                initialValue={
                    data["orderPos"]
                }
                helperText="Position of an order within the order itself if an order contains multiple orders"
                onEdit={onEdit}/>
            <EditChoiceBox label="Assigned workingpiece" mapKey="assignedWorkingPiece"
                initialValue={
                    data["assignedWorkingPiece"]
                }
                choices={workingPieces}
                helperText="Optional: Id of the assigned workingpiece. Make sure that the state of the workingpiece is correct so the workingplan is executable. If not specified the MES searches by itself for the first available piece."
                onEdit={onEdit}/>

            <EditTextBox label="Customer" mapKey="customer"
                initialValue={
                    data["customer"]
                }
                helperText="Optional: Name of the customer who assigned the order. Only change if new customer is already created as an customer"
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
            <ErrorSnackbar level={level}
                message={msg}
                isOpen={snackbarOpen}/>
        </Dialog>
    );
}
