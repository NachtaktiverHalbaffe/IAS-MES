/*
Filename: createworkingplan.js
Version name: 0.1, 2021-06-18
Short description: page for creating a workingplan

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import axios from "axios";
import { Box, Fab, List, ListItem } from "@material-ui/core";
import { makeStyles, useTheme } from "@material-ui/core/styles";
import AddIcon from "@material-ui/icons/Add";

//own costum components
import { IP_BACKEND } from "../../const";
import StateWorkingStepCard from "../../components/workingstepcard/stateworkingstepcard";
import EditStateWorkingStepDialog from "../../components/editworkingstepdialog/editworkingstepdialog";

//images
import store from "../../assets/storage.png";
import assemble from "../../assets/assemble.png";
import color from "../../assets/color.png";
import imgPackage from "../../assets/package.png";
import unpackage from "../../assets/unpackage.png";
import generic from "../../assets/generic.png";

const useStyles = makeStyles((theme) => ({
  root: {
    backgroundColor: theme.palette.background.paper,
    width: 500,
    position: "relative",
    minHeight: 200,
  },
  fab: {
    position: "absolute",
    bottom: theme.spacing(2),
    right: theme.spacing(2),
  },
}));

export default function CreateWorkingPlan() {
  const classes = useStyles();
  const [state, setState] = React.useState({
    workingPlan: [],
    workingSteps: [],
  });
  const { workingPlan, workingSteps } = state;

  // states stuff for opening and closing dialogs
  const [open, setOpen] = React.useState(false);
  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    let newWorkingSteps = workingSteps;
    newWorkingSteps.push(updatedData);
    setState({
      workingPlan: workingPlan,
      workingSteps: newWorkingSteps,
    });
    setOpen(false);
  };

  const onFabClick = () => {
    setOpen(true);
  };

  const fab = [
    {
      color: "primary",
      className: classes.fab,
      icon: <AddIcon />,
      label: "Add",
    },
  ];

  return (
    <Box width={1}>
      <List>
        {createListItem(workingPlan, workingSteps, handleClose, onSave, open)}
      </List>
      <Fab
        color="primary"
        aria-label="add"
        className={fab.className}
        onClick={onFabClick}
      >
        <AddIcon />
      </Fab>
    </Box>
  );
}

function createListItem(
  workingPlan,
  workingSteps,
  handleClose,
  onSave,
  isOpen
) {
  let items = [];
  let steps = workingSteps;
  if (steps.length > 1) {
    steps = steps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
  }
  for (let j = 0; j < steps.length; j++) {
    // get right image
    let img = null;
    if (steps[j].task === "unstore" || steps[j].task === "store") {
      img = store;
    } else if (steps[j].task === "assemble") {
      img = assemble;
    } else if (steps[j].task === "color") {
      img = color;
    } else if (steps[j].task === "generic") {
      img = generic;
    } else if (steps[j].task === "package") {
      img = imgPackage;
    } else if (steps[j].task === "unpackage") {
      img = unpackage;
    }
    // get wright order
    items.push(
      <ListItem width={1}>
        <StateWorkingStepCard
          assignedToUnit={steps[j].assignedToUnit}
          description={steps[j].description}
          name={steps[j].name}
          img={img}
          state="pending"
          task={steps[j].task}
          stepNo={steps[j].stepNo}
          color={steps[j].color}
          id={steps[j].id}
        />
        <EditStateWorkingStepDialog
          open={isOpen}
          onClose={handleClose}
          data={{
            assignedToUnit: 0,
            description: "",
            state: "pending",
            task: "",
            stepNo: 0,
            name: "",
            id: workingSteps.length + 1,
            color: "#000000",
          }}
          onSave={onSave}
        />
      </ListItem>
    );
  }

  return items;
}
