/*
Filename: stateordercard.js
Version name: 1.0, 2021-07-10
Short description: Card component for a specific order

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import axios from "axios";
import {
    Box,
    Grid,
    Paper,
    CardActionArea,
    CardContent,
    Typography
} from "@material-ui/core";

import EditStateOrderDialog from "../../editdialogs/editorderdialog/editorderdialog";
import {IP_BACKEND, AUTO_HIDE_DURATION} from ".../../../src/const";

export default function StateOrderCard(props) {
    let name = "";
    let description = "";
    let orderNo = 0;
    let orderPos = 0;
    let costumer = "";
    let assignedAt = "";
    let id = 0;
    let assignedWorkingPiece = 0;
    let costumerNo = 0;
    let allSteps = [];
    let data = new Map();


    const [open, setOpen] = React.useState(false);
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

    // apply props to internal variables
    if (props.description) {
        description = props.description;
        data["description"] = description;
    }
    if (props.name) {
        name = props.name;
        data["name"] = name;
    }
    if (props.orderNo) {
        orderNo = props.orderNo;
        data["orderNo"] = orderNo;
    }
    if (props.orderPos) {
        orderPos = props.orderPos;
        data["orderPos"] = orderPos;
    }
    if (props.costumer) {
        costumer = props.costumer;
        data["costumer"] = costumer;
    }
    if (props.assignedAt) {
        assignedAt = props.assignedAt;
        data["assignetAt"] = assignedAt;
    }
    if (props.id) {
        id = props.id;
        data["id"] = id;
    }
    if (props.costumerNo) {
        costumerNo = props.costumerNo;
        data["costumerNo"] = costumerNo;
    }
    if (props.assignedWorkingPiece) {
        assignedWorkingPiece = props.assignedWorkingPiece;
        data["assignedWorkingPiece"] = assignedWorkingPiece;
    }
    if (props.allSteps) {
        allSteps = props.allSteps;
        data["allSteps"] = allSteps;
    }

    // state managment for Dialogs
    const handleClickOpen = () => {
        setOpen(true);
    };

    const handleClose = () => {
        setOpen(false);
    };

    // update data in backend after changes over the dialog finished
    const onSave = (updatedData) => { // update data in Mes
        let costumerNo = updatedData["costumerNo"];
        if (costumerNo === 0) {
            costumerNo = null;
        }
        axios.patch("http://" + IP_BACKEND + ":8000/api/AssignedOrder/" + updatedData["id"].toString(), {
            description: updatedData["description"],
            orderNo: updatedData["orderNo"],
            orderPos: updatedData["orderPos"],
            name: updatedData["name"],
            costumer: costumerNo,
            assignedWorkingPiece: updatedData["assignedWorkingPiece"]
        });

        setErrorState({snackbarOpen: true, msg: "Sucessfully updated workingstep", level: "success"});
        return true;
    };

    // delete instance in backend if delete option in dialog was selected
    const onDelete = (orderToDelete) => {
        axios.delete("http://" + IP_BACKEND + ":8000/api/AssignedOrder/" + orderToDelete["id"].toString());
        return true;
    };

    return (
        <Box width={1}>
            <Paper elevation={3}>
                <CardActionArea onClick={handleClickOpen}>
                    <Grid container direction="row" alignItems="center" justify="flex-start"
                        width={1}>
                        <Grid item>
                            <div>&nbsp; &nbsp; &nbsp;</div>
                        </Grid>
                        <Grid item>
                            <CardContent>
                                <Typography gutterBottom variant="h5" component="h2">
                                    {name} </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Description:{" "} </Box>
                                    {" "}
                                    {description} </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Order number:{" "} </Box>
                                    {" "}
                                    {orderNo} </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Order position:{" "} </Box>
                                    {" "}
                                    {orderPos} </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Assigned workingpiece:{" "} </Box>
                                    {" "}
                                    {
                                    "Workingpiece " + assignedWorkingPiece.toString()
                                } </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Costumer:{" "} </Box>
                                    {" "}
                                    {costumer} </Typography>
                                <Typography variant="body1" color="textSecondary" component="div">
                                    <Box fontWeight="fontWeightBold" display="inline">
                                        Assigned at:{" "} </Box>
                                    {" "}
                                    {assignedAt} </Typography>
                            </CardContent>
                        </Grid>
                    </Grid>
                </CardActionArea>
                <EditStateOrderDialog open={open}
                    onClose={handleClose}
                    data={data}
                    onSave={onSave}
                    onDelete={onDelete}
                    title="Edit order"/>
            </Paper>
        </Box>
    );
}
