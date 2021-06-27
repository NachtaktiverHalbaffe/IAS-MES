/*
Filename: createworkingplan.js
Version name: 0.1, 2021-06-18
Short description: page for creating a workingplan

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useEffect } from "react";
import axios from "axios";
import {
  Box,
  Button,
  Dialog,
  DialogTitle,
  Fab,
  List,
  ListItem,
  Typography,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import AddIcon from "@material-ui/icons/Add";

//own costum components
import { IP_BACKEND, AUTO_HIDE_DURATION } from "../../const";
import StateWorkingStepCard from "../../components/cards/workingstepcard/stateworkingstepcard";
import EditTextBox from "../../components/edittextbox/edittextbox";
import EditStateWorkingStepDialog from "../../components/editdialogs/editworkingstepdialog/editworkingstepdialog";
import EditStateWorkingPlanDialog from "../../components/editdialogs/editworkingplandialog/editworkingplandialog";
import StateWorkingPlanCard from "../../components/cards/workingplancard/workingplancard";

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
    workingPlan: {
      name: "",
      description: "",
      workingPlanNo: 0,
      workingSteps: [],
    },
    workingSteps: [],
  });

  useEffect(() => {
    const pollingTime = 1; // interval for polling in seconds

    const interval = setInterval(async () => {
      // set dialog of creating an workinplan to open if not created
      if (state.workingPlan["workingPlanNo"] === 0) {
        setOpen(true);
      }
      // only poll data from backend if there are workingplans and workingsteps to poll
      if (state.workingPlan["workingPlanNo"] !== 0) {
        getWorkingPlanFromMes();
      }
      if (state.workingSteps.length !== 0) {
        getWorkingStepsFromMes();
      }
    }, pollingTime * 1000);
    return () => clearInterval(interval);
  });

  const [wsopen, setWSOpen] = React.useState(false);
  // states stuff for opening and closing dialogs
  const [open, setOpen] = React.useState(true);
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
    setOpen(false);
  };

  const handleWSClose = () => {
    setWSOpen(false);
  };

  const addItem = (updatedData) => {
    // set some params and validate other params
    let opNo = 0;
    if (updatedData["task"] === "store") {
      opNo = 210;
    } else if (updatedData["task"] === "unstore") {
      opNo = 213;
    } else if (
      updatedData["task"] === "color" ||
      updatedData["task"] === "package" ||
      updatedData["task"] === "unpackage" ||
      updatedData["task"] === "assemble" ||
      updatedData["task"] === "generic"
    ) {
      opNo = 510;
    } else {
      setErrorState({
        snackbarOpen: true,
        msg: "Internal error: Couldnt assign task a operation number",
        level: "warning",
      });
      return false;
    }

    //update data in Mes
    let payload = {};
    if (updatedData["description"] !== "") {
      payload = {
        name: updatedData["name"],
        description: updatedData["description"],
        task: updatedData["task"],
        color: updatedData["color"],
        stepNo: updatedData["stepNo"],
        operationNo: opNo,
        assignedToUnit: updatedData["assignedToUnit"],
      };
    } else {
      payload = {
        name: updatedData["name"],
        task: updatedData["task"],
        color: updatedData["color"],
        stepNo: updatedData["stepNo"],
        operationNo: opNo,
        assignedToUnit: updatedData["assignedToUnit"],
      };
    }
    // send workingplan to mes
    axios
      .post("http://" + IP_BACKEND + ":8000/api/WorkingStep/", payload)
      .then(async (res) => {
        // create list of workingstep ids for workingplan because
        // in the backend workingsteps and workingplan are linked
        // with a many to many relationship which are represented as
        // ids.
        let workingSteps = state.workingSteps.concat(res.data);
        let wsIds = [];
        for (let i = 0; i < workingSteps.length; i++) {
          wsIds.push(workingSteps[i]["id"]);
        }
        let workingPlan = state.workingPlan;
        workingPlan["workingSteps"] = wsIds;
        // update workingplan in mes
        let payload = {
          workingSteps: wsIds,
        };
        axios
          .patch(
            "http://" +
              IP_BACKEND +
              ":8000/api/WorkingPlan/" +
              state.workingPlan.workingPlanNo.toString(),
            payload
          )
          .then((res) => {
            setState({
              workingPlan: res.data,
              workingSteps: workingSteps,
            });
          });
      });

    return true;
  };

  const createPlan = (data) => {
    let payload = {};
    if (data["description"] !== "") {
      payload = {
        name: data["name"],
        description: data["description"],
        workingPlanNo: parseInt(data["workingPlanNo"]),
        workingSteps: [],
      };
    } else {
      payload = {
        name: data["name"],
        workingPlanNo: parseInt(data["workingPlanNo"]),
        workingSteps: [],
      };
    }
    axios
      .post("http://" + IP_BACKEND + ":8000/api/WorkingPlan/", payload)
      .then((res) => {
        setState({
          workingPlan: res.data,
          workingSteps: state.workingSteps,
        });
      });
    setErrorState({
      snackbarOpen: true,
      msg: "Successfully created workingplan",
      level: "success",
    });
    return true;
  };

  function getWorkingPlanFromMes() {
    let plan = null;
    axios
      .get(
        "http://" +
          IP_BACKEND +
          ":8000/api/WorkingPlan/" +
          state.workingPlan.workingPlanNo.toString()
      )
      .then(async (res) => {
        plan = res.data;
        await setState({
          workingPlan: plan,
          workingSteps: state.workingSteps,
        });
      });
  }

  async function getWorkingStepsFromMes() {
    let steps = [];
    let oldSteps = state.workingSteps;
    for (let i = 0; i < state.workingPlan["workingSteps"].length; i++) {
      axios
        .get(
          "http://" +
            IP_BACKEND +
            ":8000/api/WorkingStep/" +
            state.workingPlan["workingSteps"][i].toString()
        )
        .then(async (res) => {
          steps.push(res.data);
          // only set state if workingsteps have changed
          if (steps.length === oldSteps.length) {
            if (!mCompareWorkingSteps(oldSteps, steps)) {
              setState({
                workingPlan: state.workingPlan,
                workingSteps: steps,
              });
            }
          }
        });
    }
  }

  const fab = [
    {
      color: "primary",
      className: classes.fab,
      icon: <AddIcon />,
      label: "Add",
    },
  ];

  return (
    <Box>
      <Typography gutterBottom variant="h5" component="h2">
        Create workingplan (changes gets autosaved)
      </Typography>
      <EditStateWorkingPlanDialog
        data={{
          name: "",
          description: "",
          workingPlanNo: 0,
        }}
        onSave={createPlan}
        open={open}
        onClose={handleClose}
        title="Create workingplan"
      />
      <List width={1}>
        {createListItem(state.workingPlan, state.workingSteps)}
      </List>
      <Fab
        color="primary"
        aria-label="add"
        className={fab.className}
        onClick={() => {
          setWSOpen(true);
        }}
      >
        <AddIcon />
      </Fab>
      <EditStateWorkingStepDialog
        data={{
          assignedToUnit: 0,
          description: "",
          state: "pending",
          task: "",
          stepNo: 0,
          name: "",
          id: state.workingSteps.length + 1,
          color: "#000000",
        }}
        title="Create workingstep"
        onSave={addItem}
        open={wsopen}
        onClose={handleWSClose}
      />
    </Box>
  );
}

function createListItem(workingPlan, workingSteps) {
  let items = [];
  let steps = workingSteps;
  if (workingPlan["workingPlanNo"] !== 0) {
    items.push(
      <ListItem width={1}>
        <StateWorkingPlanCard
          name={workingPlan["name"]}
          description={workingPlan["description"]}
          workingPlanNo={workingPlan["workingPlanNo"]}
        />
      </ListItem>
    );
  }

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
      <ListItem width={1} key={steps[j].id}>
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
      </ListItem>
    );
  }

  return items;
}

// compares if two states of Workingsteps are equal. Returns true if equal and vise versa
function mCompareWorkingSteps(oldSteps, newSteps) {
  // check lengths

  if (oldSteps.length !== newSteps.length) {
    return false;
  }
  // check workingsteps
  oldSteps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
  newSteps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
  for (let i = 0; i < oldSteps.length; i++) {
    if (oldSteps[i].task !== newSteps[i].task) {
      return false;
    }
    if (oldSteps[i].color !== newSteps[i].color) {
      return false;
    }
    if (oldSteps[i].assignedToUnit !== newSteps[i].assignedToUnit) {
      return false;
    }
    if (oldSteps[i].name !== newSteps[i].name) {
      return false;
    }
    if (oldSteps[i].description !== newSteps[i].description) {
      return false;
    }
  }

  return true;
}
