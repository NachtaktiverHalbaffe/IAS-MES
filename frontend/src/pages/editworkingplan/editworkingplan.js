/*
Filename: editworkingplan.js
Version name: 1.0, 2021-07-10
Short description: page for editing a workingplan

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useEffect } from "react";
import axios from "axios";
import {
  Button,
  Box,
  Fab,
  Grid,
  List,
  ListItem,
  Typography,
} from "@material-ui/core";
import AddIcon from "@material-ui/icons/Add";

//own costum components
import EditStateWorkingStepDialog from "../../components/editdialogs/editworkingstepdialog/editworkingstepdialog";
import ChooseWorkingPlanDialog from "../../components/editdialogs/chooseworkingplandialog/chooseworkingplandialog";
import StateWorkingStepCard from "../../components/cards/workingstepcard/stateworkingstepcard";
import StateWorkingPlanCard from "../../components/cards/workingplancard/workingplancard";
import { IP_BACKEND, AUTO_HIDE_DURATION } from "../../const";
import validateWorkingsteps from "../../components/validateworkingsteps/validateworkingsteps";
import ErrorSnackbar from "../../components/errorsnackbar/errorsnackbar";

//images
import store from "../../assets/storage.png";
import assemble from "../../assets/assemble.png";
import color from "../../assets/color.png";
import imgPackage from "../../assets/package.png";
import unpackage from "../../assets/unpackage.png";
import generic from "../../assets/generic.png";

export default function EditWorkingPlan() {
  const [state, setState] = React.useState({
    workingPlans: [],
  });
  const [selectedWorkingplan, setSelectedWorkingplan] = React.useState({
    workingPlan: {
      name: "",
      description: "",
      workingPlanNo: 0,
      workingSteps: [],
    },
    workingSteps: [],
  });
  const [open, setOpen] = React.useState(true);
  const [wsopen, setWSOpen] = React.useState(false);
  const [errorState, setErrorState] = React.useState({
    snackbarOpen: false,
    msg: "",
    level: "",
  });
  // close snackbar after AUTO_HIDE_DURATION exceeded
  React.useEffect(() => {
    setTimeout(() => {
      if (errorState.snackbarOpen) {
        setErrorState({
          snackbarOpen: false,
          msg: "",
          level: "",
        });
      }
    }, AUTO_HIDE_DURATION);
  });

  // poll data from backend
  useEffect(() => {
    const pollingTime = 1; // interval for polling in seconds

    const interval = setInterval(async () => {
      // set dialog of creating an workinplan to open if not created
      if (selectedWorkingplan.workingPlan["workingPlanNo"] === 0) {
        setOpen(true);
      }
      getWorkingPlansFromMes();
      if (selectedWorkingplan.workingPlan["workingPlanNo"] !== 0) {
        getWorkingPlanFromMes();
      }
    }, pollingTime * 1000);
    return () => clearInterval(interval);
  });

  // callback function when a workingplan is selected from the choose workingplan dialog
  const selectWorkingPlan = (selectedPlan) => {
    setSelectedWorkingplan({
      workingPlan: selectedPlan,
      workingSteps: selectedWorkingplan.workingSteps,
    });
    setOpen(false);
    return true;
  };

  // callback function when a workingplan is selected from the choose workingplan dialog
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
      return false;
    }
    let newSteps = selectedWorkingplan.workingSteps.concat(updatedData);
    let validator = validateWorkingsteps(newSteps);
    let isValid = validator[0];
    let errormsg = validator[1];
    if (isValid) {
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
          let workingSteps = selectedWorkingplan.workingSteps.concat(res.data);
          let wsIds = [];
          for (let i = 0; i < workingSteps.length; i++) {
            wsIds.push(workingSteps[i]["id"]);
          }
          let workingPlan = selectedWorkingplan.workingPlan;
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
                selectedWorkingplan.workingPlan.workingPlanNo.toString(),
              payload
            )
            .then((res) => {
              setSelectedWorkingplan({
                workingPlan: res.data,
                workingSteps: workingSteps,
              });
            });
        });

      return true;
    } else {
      setErrorState({
        snackbarOpen: true,
        msg: errormsg,
        level: "warning",
      });
      return false;
    }
  };

  function getWorkingPlansFromMes() {
    axios
      .get("http://" + IP_BACKEND + ":8000/api/WorkingPlan/")
      .then(async (res) => {
        let plans = res.data;
        await setState({
          workingPlans: plans,
        });
        getWorkingStepsFromMes();
      });
  }

  function getWorkingPlanFromMes() {
    axios
      .get(
        "http://" +
          IP_BACKEND +
          ":8000/api/WorkingPlan/" +
          selectedWorkingplan.workingPlan["workingPlanNo"]
      )
      .then(async (res) => {
        setSelectedWorkingplan({
          workingPlan: res.data,
          workingSteps: selectedWorkingplan.workingSteps,
        });
      })
      .catch((err) => {
        setSelectedWorkingplan({
          workingPlan: {
            name: "",
            description: "",
            workingPlanNo: 0,
            workingSteps: [],
          },
          workingSteps: [],
        });
      });
  }

  async function getWorkingStepsFromMes() {
    let steps = [];
    let oldSteps = selectedWorkingplan.workingSteps;

    for (
      let i = 0;
      i < selectedWorkingplan.workingPlan["workingSteps"].length;
      i++
    ) {
      axios
        .get(
          "http://" +
            IP_BACKEND +
            ":8000/api/WorkingStep/" +
            parseInt(selectedWorkingplan.workingPlan["workingSteps"][i])
        )
        .then(async (res) => {
          steps.push(res.data);
          if (
            steps.length ===
            selectedWorkingplan.workingPlan["workingSteps"].length
          ) {
            if (!mCompareWorkingSteps(oldSteps, steps)) {
              setSelectedWorkingplan({
                workingPlan: selectedWorkingplan.workingPlan,
                workingSteps: steps,
              });
            }
          }
        });
    }
  }

  return (
    <Box justify="center" alignItems="center">
      <Grid
        container
        justify="space-evenly"
        alignItems="center"
        direction="column"
      >
        <Typography gutterBottom variant="h5" component="h2">
          Edit workingplan
        </Typography>
        <Grid item>
          <div>&nbsp; &nbsp; &nbsp;</div>
        </Grid>
        <List>
          {createListItem(
            selectedWorkingplan.workingPlan,
            selectedWorkingplan.workingSteps
          )}
          <EditStateWorkingStepDialog
            data={{
              assignedToUnit: 0,
              description: "",
              state: "pending",
              task: "",
              stepNo: (selectedWorkingplan.workingSteps.length + 1) * 10,
              name: "",
              id: selectedWorkingplan.workingSteps.length + 1,
              color: "#000000",
            }}
            title="Create workingstep"
            onSave={addItem}
            open={wsopen}
            clearDialogOnSave={true}
            onClose={() => {
              setWSOpen(false);
            }}
          />
        </List>
        <Grid item>
          <div>&nbsp; &nbsp; &nbsp;</div>
          <Fab
            aria-label="add"
            color="secondary"
            onClick={() => {
              setWSOpen(true);
            }}
          >
            <AddIcon />
          </Fab>
          <div>&nbsp; &nbsp; &nbsp;</div>
        </Grid>
        <Grid item>
          <Button
            justify="flex-end"
            variant="outlined"
            color="secondary"
            onClick={() => {
              setOpen(true);
            }}
          >
            Select workingplan
          </Button>
        </Grid>
        <ChooseWorkingPlanDialog
          open={open}
          selectWorkingPlan={selectWorkingPlan}
          title="Choose workingplan to edit"
          onClose={() => {
            setOpen(false);
          }}
          workingPlans={state.workingPlans}
        />
      </Grid>
      <ErrorSnackbar
        level={errorState.level}
        message={errorState.msg}
        isOpen={errorState.snackbarOpen}
      />
    </Box>
  );
}

// create cards for workingplan and workingsteps
// @return:
//    items: list of workingplancard and workingstepcards
function createListItem(workingPlan, workingSteps) {
  let items = [];
  let steps = workingSteps;
  if (workingPlan["workingPlanNo"] !== 0) {
    items.push(
      <Grid item>
        <StateWorkingPlanCard
          name={workingPlan["name"]}
          description={workingPlan["description"]}
          workingPlanNo={workingPlan["workingPlanNo"]}
          workingSteps={workingPlan["workingSteps"]}
        />
      </Grid>
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
      <ListItem>
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
          allSteps={steps}
        />
      </ListItem>
    );
  }

  return items;
}

// compares if two states of Workingsteps are equal. Returns true if equal and vise versa
// @params:
//    oldSteps: current Steps saved in state
//    newSteps: steps polled from backend
// @return:
//    if workingsteps changed (false) or are the same (true)
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
