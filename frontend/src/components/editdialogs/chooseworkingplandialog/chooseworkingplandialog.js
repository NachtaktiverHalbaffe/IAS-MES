/*
Filename: createorder.js
Version name: 0.1, 2021-06-18
Short description: page for creating a order

(C) 2003-2021 IAS, Universitaet Stuttgart

*/
import React from "react";
import {
  Button,
  Card,
  Dialog,
  DialogTitle,
  List,
  ListItem,
} from "@material-ui/core";

import StateWorkingPlanCard from "../../cards/workingplancard/workingplancard";

export default function ChooseWorkingPlanDialog(props) {
  const { workingPlans, title, open, onClose, selectWorkingPlan } = props;

  const handleClose = () => {
    onClose();
  };

  return (
    <Dialog
      onClose={handleClose}
      aria-labelledby="simple-dialog-title"
      open={open}
    >
      <DialogTitle id="simple-dialog-title">{title}</DialogTitle>
      <List>{createSelectWorkingPlan(workingPlans, selectWorkingPlan)}</List>
    </Dialog>
  );
}

function createSelectWorkingPlan(workingPlans, selectWorkingPlan) {
  let items = [];

  if (workingPlans.length > 1) {
    workingPlans = workingPlans.sort((a, b) =>
      a.workingPlanNo > b.workingPlanNo ? 1 : -1
    );
  }
  for (let i = 0; i < workingPlans.length; i++) {
    items.push(
      <ListItem width={1}>
        <Card>
          <StateWorkingPlanCard
            name={workingPlans[i]["name"]}
            description={workingPlans[i]["description"]}
            workingPlanNo={workingPlans[i]["workingPlanNo"]}
            workingSteps={workingPlans[i]["workingSteps"]}
            onClick={selectWorkingPlan}
          />
        </Card>
      </ListItem>
    );
  }

  return items;
}
