/*
Filename: workingplancard.js
Version name: 1.0, 2021-07-10
Short description: Card component for a specific workingplan

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

import ErrorSnackbar from "../../errorsnackbar/errorsnackbar";
import EditStateWorkingPlanDialog from "../../editdialogs/editworkingplandialog/editworkingplandialog";
import {IP_BACKEND, AUTO_HIDE_DURATION} from ".../../../src/const";

export default function StateWorkingPlanCard(props) {
    let name = "";
    let description = "";
    let workingPlanNo = 0;
    let workingSteps;
    let handleClickOpen = null;
    let onClick = null;
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
    if (props.description) {
        description = props.description;
        data["description"] = description;
    }
    if (props.name) {
        name = props.name;
        data["name"] = name;
    }
    if (props.workingPlanNo) {
        workingPlanNo = props.workingPlanNo;
        data["workingPlanNo"] = workingPlanNo;
    }
    if (props.workingSteps) {
        workingSteps = props.workingSteps;
        data["workingSteps"] = workingSteps;
    }
    if (! props.onClick) {
        handleClickOpen = () => {
            setOpen(true);
        };
    } else {
        onClick = props.onClick;
        handleClickOpen = () => {
            onClick(data);
        };
    }

    // state managment for Dialogs
    const handleClose = (data) => {
        setOpen(false);
    };

    // update data in backend after changes over the dialog finished
    const onSave = (updatedData) => {
        let payload = {};
        if (updatedData["description"] !== "") {
            payload = {
                name: updatedData["name"],
                description: updatedData["description"],
                workingPlanNo: parseInt(updatedData["workingPlanNo"])
            };
        } else {
            payload = {
                name: updatedData["name"],
                workingPlanNo: parseInt(updatedData["workingPlanNo"])
            };
        }
        axios.patch("http://" + IP_BACKEND + ":8000/api/WorkingPlan/" + updatedData["workingPlanNo"].toString(), payload);
        setErrorState({snackbarOpen: true, msg: "Successfully edited workingplan", level: "success"});
        return true;
    };

    // delete instance in backend if delete option in dialog was selected
    const onDelete = (planToDelete) => { // delete corresponding workingsteps from database
        console.log(planToDelete);
        for (let i = 0; i < planToDelete["workingSteps"].length; i++) {
            axios.delete("http://" + IP_BACKEND + ":8000/api/WorkingStep/" + planToDelete["workingSteps"][i].toString());
        }
        // delete workingplan itself
        axios.delete("http://" + IP_BACKEND + ":8000/api/WorkingPlan/" + planToDelete["workingPlanNo"].toString());
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
                                        Workingplan number:{" "} </Box>
                                    {" "}
                                    {workingPlanNo} </Typography>
                            </CardContent>
                        </Grid>
                    </Grid>
                </CardActionArea>
                <EditStateWorkingPlanDialog open={open}
                    onClose={handleClose}
                    data={data}
                    onSave={onSave}
                    onDelete={onDelete}
                    title="Edit workingplan"/>
            </Paper>
            <ErrorSnackbar level={level}
                message={msg}
                isOpen={snackbarOpen}/>
        </Box>
    );
}
