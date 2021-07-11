/*
Filename: stateworkingpiececard.js
Version name: 1.0, 2021-07-10
Short description: Card component for a specific state of a workingpiece

(C) 2003-2021 IAS, Universitaet Stuttgart

*/
import axios from "axios";
import React from "react";
import Box from "@material-ui/core/Box";
import {
    Checkbox,
    Grid,
    Paper,
    ListItem,
    Dialog,
    DialogTitle,
    CardContent,
    CardActionArea,
    Button,
    Typography
} from "@material-ui/core";
import {ChromePicker} from "react-color";

import EditTextBox from "../../edittextbox/edittextbox";
import EditCheckBox from "../../edittextbox/editcheckbox";
import EditChoiceBox from "../../edittextbox/editchoicebox";
import ErrorSnackbar from "../../errorsnackbar/errorsnackbar";
import {IP_BACKEND, AUTO_HIDE_DURATION, DEFINED_MODELS} from ".../../../src/const";

export default function StateWorkingPieceCard(props) {
    let id = 0;
    let location = "";
    let partNo = "";
    let carrierId = "";
    let storageLocation = "";
    let color = "";
    let isAssembled = false;
    let isPackaged = false;
    let model = "";
    let data = new Map();

    const [open, setOpen] = React.useState(false);
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

    // apply props to internal variables
    if (props.id) {
        id = props.id;
        data["id"] = id;
    }
    if (props.location) {
        location = props.location;
        data["location"] = location;
    }
    if (props.partNo) {
        partNo = props.partNo;
        data["partNo"] = partNo;
    }
    if (props.carrierId) {
        carrierId = props.carrierId;
        data["carrierId"] = carrierId;
    }
    if (props.storageLocation) {
        storageLocation = props.storageLocation;
        data["storageLocation"] = storageLocation;
    }

    if (props.storageLocation) {
        storageLocation = props.storageLocation;
        data["storageLocation"] = storageLocation;
    }
    if (props.color) {
        color = props.color;
        data["color"] = color;
    }

    if (props.isAssembled) {
        isAssembled = props.isAssembled;
        data["isAssembled"] = isAssembled;
    }

    if (props.isPackaged) {
        isPackaged = props.isPackaged;
        data["isPackaged"] = isPackaged;
    }
    if (props.model) {
        model = props.model;
        data["model"] = model;
    }

    // state managment for Dialogs
    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    // update data in backend after changes over the dialog finished
    const onSave = (updatedData) => { // validate if location is a possible resource
        if (updatedData["location"] < 1 || updatedData["location"] > 10 || isNaN(updatedData["location"])) {
            setErrorState({snackbarOpen: true, msg: "Invalid location. Location must be an existing resource id between 1-10", level: "warning"});
            return false;
        }
        // validate storage location
        if (updatedData["storageLocation"] < 1 || updatedData["storageLocation"] > 30 || isNaN(updatedData["storageLocation"])) {
            setErrorState({snackbarOpen: true, msg: "Invalid location. Location must be between 1-30", level: "warning"});
            return false;
        }
        if (!/^#[0-9A-F]{6}$/i.test(updatedData["color"])) {
            // validate if color os valid hexcolor
            // expression !/^#[0-9A-F]{6}$/i:
            // ^# check if first char is #
            // [0-9A-F]{6} check if next 6 characters are 0-9 or a-f
            setErrorState({snackbarOpen: true, msg: "Color is not formatted as a hex color. Format: #0dccff", level: "warning"});
            return false;
        }
        // update data in Mes
        axios.patch("http://" + IP_BACKEND + ":8000/api/StateWorkingPiece/" + updatedData["id"].toString(), {
            location: updatedData["location"],
            partNo: updatedData["partNo"],
            carrierId: updatedData["carrierId"],
            storageLocation: updatedData["storageLocation"],
            color: updatedData["color"],
            isAssembled: updatedData["isAssembled"],
            isPackaged: updatedData["isPackaged"],
            model: updatedData["model"]
        });
        setErrorState({snackbarOpen: true, msg: "Successfully updated state of workingPiece", level: "success"});
        return true;
    };

    // delete instance in backend if delete option in dialog was selected
    const onDelete = (orderToDelete) => {
        axios.delete("http://" + IP_BACKEND + ":8000/api/StateWorkingPiece/" + orderToDelete["id"].toString());
        return true;
    };

    return (
        <Box width={1}>
            <Paper elevation={3}>
                <CardActionArea onClick={handleClickOpen}>
                    <Grid container direction="row" alignItems="center" justify="space-evenly" width="1000px">
                        <Grid item>
                            <CardContent>
                                <Typography gutterBottom variant="h5" component="h2">
                                    {
                                    "Workingpiece number " + id.toString()
                                } </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Typography variant="body1" color="textSecondary" component="div">
                                        <Box fontWeight="fontWeightBold" display="inline">
                                            Id:{" "} </Box>
                                        {" "}
                                        {id} </Typography>
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Location:{" "} </Box>
                                    {" "}
                                    {location} </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Location in storage:{" "} </Box>
                                    {" "}
                                    {storageLocation} </Typography>

                                <Typography variant="body1" component="div" color="textSecondary">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Color:{" "} </Box>
                                    {" "}
                                    {color}
                                    <Box color={color}
                                        width={10}
                                        height={10}
                                        display="inline">
                                        {"    ♦"} </Box>
                                </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        3D-Model:{" "} </Box>
                                    {" "}
                                    {model} </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Assembled:{" "} </Box>
                                    {" "}
                                    <Checkbox checked={isAssembled}
                                        onChange={
                                            () => {}
                                        }
                                        name="checkedB"
                                        color="primary"/>
                                </Typography>
                            <Typography variant="body1" color="textSecondary" component="div">
                                <Box fontWeight="fontWeightBold" display="inline">
                                    Packaged:{" "} </Box>
                                {" "}
                                <Checkbox checked={isPackaged}
                                    onChange={
                                        () => {}
                                    }
                                    name="checkedB"
                                    color="primary"/>
                            </Typography>
                    </CardContent>
                </Grid>
            </Grid>
        </CardActionArea>
        <EditStateWorkingPieceDialog open={open}
            onClose={handleClose}
            onSave={onSave}
            onDelete={onDelete}
            data={data}/>
    </Paper>
    <ErrorSnackbar level={level}
        message={msg}
        isOpen={snackbarOpen}/>
</Box>
    );
}

// Dialog for editing state of workingpiece
function EditStateWorkingPieceDialog(props) {
    const {
        onClose,
        onSave,
        onDelete,
        open,
        data
    } = props;
    const [state, setState] = React.useState(data);
    const [color, setColor] = React.useState(data["color"]);

    // for closing dialog
    const handleClose = () => {
        onClose();
    };

    // callback when save button is pressed
    const handleSave = () => {
        if (onSave(state)) {
            handleClose();
        }
    };

    // callback when delete button is pressed
    const handleDelete = () => {
        if (onDelete(state)) {
            handleClose();
            return true;
        }
    };

    // change state of card when a value gets changed
    const onEdit = (key, value) => {
        let newState = state;
        newState[key] = value;
        setState(newState);
    };

    // change state of card when color from colorpicker gets changed
    const onColorEdit = (value) => {
        let newState = state;
        newState["color"] = value.hex;
        setState(newState);
        setColor(value.hex);
    };

    return (
        <Dialog onClose={handleClose}
            aria-labelledby="simple-dialog-title"
            open={open}
            justify="center">
            <DialogTitle id="simple-dialog-title">
                Edit state of workingpiece
            </DialogTitle>
            <Grid container direction="column" justify="center" alignItems="center">
                <EditTextBox label="Location" mapKey="location"
                    initialValue={
                        data["location"]
                    }
                    helperText="Location of the workingpiece (resourceId)"
                    onEdit={onEdit}/>
                <EditTextBox label="Location in storage" mapKey="storageLocation"
                    initialValue={
                        data["storageLocation"]
                    }
                    helperText="Location in storage of the workingpiece (resourceId)"
                    onEdit={onEdit}/>
                <Grid item>
                    <Typography gutterBottom component="h4">
                        {"Color"} </Typography>
                    <ChromePicker color={color}
                        onChangeComplete={onColorEdit}/>
                </Grid>
                <EditCheckBox label="Assembled" mapKey="isAssembled"
                    initialValue={
                        data["isAssembled"]
                    }
                    helperText="If workingpiece is assembled"
                    onEdit={onEdit}/>
                <EditCheckBox label="Packaged" mapKey="isPackaged"
                    initialValue={
                        data["isPackaged"]
                    }
                    helperText="If workingpiece is packaged"
                    onEdit={onEdit}/>
                <EditChoiceBox label="3D-Model" mapKey="model"
                    choices={DEFINED_MODELS}
                    initialValue={
                        data["model"]
                    }
                    helperText="Selected 3D-Model of the workingpiece"
                    onEdit={onEdit}/>
                <ListItem justify="flex-end">
                    <Button justify="flex-end" variant="outlined" color="primary" href="#outlined-buttons"
                        onClick={handleSave}>
                        Save
                    </Button>
                    <div>&nbsp; &nbsp; &nbsp;</div>
                    <Button justify="flex-end" variant="outlined" color="primary" href="#outlined-buttons"
                        onClick={handleDelete}>
                        Delete
                    </Button>
                </ListItem>
            </Grid>
        </Dialog>
    );
}
