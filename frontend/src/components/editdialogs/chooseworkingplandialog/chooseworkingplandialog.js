/*
Filename: chooseworkingplandialog.js
Version name: 1.0, 2021-07-10
Short description: dialog for choosing a workingplan from all existing workingplans

(C) 2003-2021 IAS, Universitaet Stuttgart

*/
import React from "react";
import {
    Card,
    Dialog,
    DialogTitle,
    List,
    ListItem
} from "@material-ui/core";

import StateWorkingPlanCard from "../../cards/workingplancard/workingplancard";

export default function ChooseWorkingPlanDialog(props) {
    const {
        workingPlans,
        title,
        open,
        onClose,
        selectWorkingPlan
    } = props;

    // callback when dialog is closed
    const handleClose = () => {
        onClose();
    };

    return (
        <Dialog onClose={handleClose}
            aria-labelledby="simple-dialog-title"
            open={open}>
            <DialogTitle id="simple-dialog-title">
                {title}</DialogTitle>
            <List>{
                createSelectWorkingPlan(workingPlans, selectWorkingPlan)
            }</List>
        </Dialog>
    );
}

// create list of cards of all workingplans
function createSelectWorkingPlan(workingPlans, selectWorkingPlan) {
    let items = [];

    // sort workingplans
    if (workingPlans.length > 1) {
        workingPlans = workingPlans.sort((a, b) => a.workingPlanNo > b.workingPlanNo ? 1 : -1);
    }
    for (let i = 0; i < workingPlans.length; i++) {
        items.push (
            <ListItem width={1}
                key={
                    workingPlans[i]["workingPlanNo"]
            }>
                <Card>
                    <StateWorkingPlanCard name={
                            workingPlans[i]["name"]
                        }
                        description={
                            workingPlans[i]["description"]
                        }
                        workingPlanNo={
                            workingPlans[i]["workingPlanNo"]
                        }
                        workingSteps={
                            workingPlans[i]["workingSteps"]
                        }
                        onClick={selectWorkingPlan}/>
                </Card>
            </ListItem>
        );
    }

    return items;
}
