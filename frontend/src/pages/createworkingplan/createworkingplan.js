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
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import AddIcon from "@material-ui/icons/Add";

//own costum components
import { IP_BACKEND, AUTO_HIDE_DURATION, DEFINED_TASKS } from "../../const";
import StateWorkingStepCard from "../../components/workingstepcard/stateworkingstepcard";
import EditTextBox from "../../components/edittextbox/edittextbox";
import ErrorSnackbar from "../../components/errorsnackbar/errorsnackbar";
import StateWorkingPlanCard from "../../components/workingplancard/workingplancard";

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

  // states stuff for opening and closing dialogs
  const [open, setOpen] = React.useState(false);
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

  const addItem = (updatedData) => {
    // set some params and validate other params
    let opNo = 0;
    //task name valid? (defined in DEFINED_TASKS and model in backend)
    if (!DEFINED_TASKS.includes(updatedData["task"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Unkown tasks. Defined tasks: " + DEFINED_TASKS.toString(),
        level: "warning",
      });
      return false;
    }
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
    //validate stepNo. It has to be a multiple of 10
    if (updatedData["stepNo"] % 10 !== 0) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid step number. Step number must be a multiple of 10",
        level: "warning",
      });
      return false;
    }
    // validate if color os vaslid hexcolor
    //expression !/^#[0-9A-F]{6}$/i:
    // ^# check if first char is #
    // [0-9A-F]{6} check if next 6 characters are 0-9 or a-f
    if (!/^#[0-9A-F]{6}$/i.test(updatedData["color"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Color is not formatted as a hex color. Format: #0dccff",
        level: "warning",
      });
      return false;
    }
    // validate if name is shorter than 30 characters
    if (updatedData["name"].length > 30) {
      setErrorState({
        snackbarOpen: true,
        msg: "Name is too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    // validate if description is shorter than 200 character
    if (updatedData["description"] > 200) {
      setErrorState({
        snackbarOpen: true,
        msg: "Description is too long.Max length: 200",
        level: "warning",
      });
      return false;
    }
    if (
      isNaN(updatedData["assignedToUnit"]) ||
      updatedData["assignedToUnit"] < 1 ||
      updatedData["assignedToUnit"] > 6
    ) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid resourceId of assigned unit. Value must be between 1-6",
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
    setErrorState({
      snackbarOpen: true,
      msg: "Sucessfully added workingstep",
      level: "success",
    });
    return true;
  };

  const createPlan = (data) => {
    if (data["name"].length > 30) {
      setErrorState({
        snackbarOpen: true,
        msg: "Name too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    if (data["description"].length > 200) {
      setErrorState({
        snackbarOpen: true,
        msg: "Description too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    if (isNaN(data["workingPlanNo"]) || data["workingPlanNo"] < 1) {
      setErrorState({
        snackbarOpen: true,
        msg: "Workingplan isnt a positive number",
        level: "warning",
      });
      return false;
    }
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

  return (
    <Box width={1}>
      <CreateWorkingPlanDialog
        data={{
          name: "",
          description: "",
          workingPlanNo: 0,
        }}
        onSave={createPlan}
        open={open}
        handleClose={handleClose}
      />
      <List width={1}>
        {createListItem(state.workingPlan, state.workingSteps)}
      </List>
      <CreateWorkingStepDialog
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
        onSave={addItem}
      />
      <ErrorSnackbar level={level} message={msg} isOpen={snackbarOpen} />
    </Box>
  );
}

function createListItem(workingPlan, workingSteps) {
  let items = [];
  let steps = workingSteps;
  if (workingPlan["workingPlanNo"] !== 0) {
    items.push(
      <StateWorkingPlanCard
        name={workingPlan["name"]}
        description={workingPlan["description"]}
        workingPlanNo={workingPlan["workingPlanNo"]}
      />
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

function CreateWorkingStepDialog(props) {
  const classes = useStyles();
  const { onSave, data } = props;
  const [open, setOpen] = React.useState(false);
  const [state, setState] = React.useState(data);

  const handleClose = () => {
    setOpen(false);
  };

  const handleSave = () => {
    if (onSave(state)) {
      handleClose();
    }
  };

  const onEdit = (key, value) => {
    let newState = state;

    newState[key] = value;
    setState(newState);
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
    <Box>
      <Fab
        color="primary"
        aria-label="add"
        className={fab.className}
        onClick={() => {
          setOpen(true);
        }}
      >
        <AddIcon />
      </Fab>

      <Dialog
        onClose={handleClose}
        aria-labelledby="simple-dialog-title"
        open={open}
      >
        <DialogTitle id="simple-dialog-title">Create workingstep</DialogTitle>
        <EditTextBox
          label="Name"
          mapKey="name"
          initialValue={data["name"]}
          helperText="Name of the workingstep"
          onEdit={onEdit}
        />
        <EditTextBox
          label="Task"
          mapKey="task"
          initialValue={data["task"]}
          helperText="Task which gets executed on the resource"
          onEdit={onEdit}
        />
        <EditTextBox
          label="Description"
          mapKey="description"
          initialValue={data["description"]}
          helperText="Description of the workingstep(optional)"
          onEdit={onEdit}
        />
        <EditTextBox
          label="Step number"
          mapKey="stepNo"
          initialValue={data["stepNo"]}
          helperText="Step number of the workingstep. Workingsteps gets executed in ascending order"
          onEdit={onEdit}
        />
        <EditTextBox
          label="State"
          mapKey="state"
          initialValue={data["state"]}
          helperText="If workingstep is pending or finished"
          onEdit={onEdit}
        />
        <EditTextBox
          label="Assigned resource"
          mapKey="assignedToUnit"
          initialValue={data["assignedToUnit"]}
          helperText="Id of assigned resource and mounted visualisation unit of the workingstep"
          onEdit={onEdit}
        />
        <ListItem justify="flex-end">
          <Button
            justify="flex-end"
            variant="outlined"
            color="primary"
            href="#outlined-buttons"
            onClick={handleSave}
          >
            Save
          </Button>
        </ListItem>
      </Dialog>
    </Box>
  );
}

function CreateWorkingPlanDialog(props) {
  const { onSave, data, handleClose, open } = props;
  const [state, setState] = React.useState(data);

  const handleSave = () => {
    if (onSave(state)) {
      handleClose();
    }
  };

  const onEdit = (key, value) => {
    let newState = state;

    newState[key] = value;
    setState(newState);
  };

  return (
    <Box>
      <Dialog
        onClose={handleClose}
        aria-labelledby="simple-dialog-title"
        open={open}
      >
        <DialogTitle id="simple-dialog-title">Create workingplan</DialogTitle>
        <EditTextBox
          label="Name"
          mapKey="name"
          initialValue={data["name"]}
          helperText="Name of the workingplan"
          onEdit={onEdit}
        />
        <EditTextBox
          label="Description"
          mapKey="description"
          initialValue={data["description"]}
          helperText="Description of the workingplan(optional)"
          onEdit={onEdit}
        />
        <EditTextBox
          label="Workingplan number"
          mapKey="workingPlanNo"
          initialValue={data["workingPlanNo"]}
          helperText="Number of the workingplan. Identifies the workingplan"
          onEdit={onEdit}
        />
        <ListItem justify="flex-end">
          <Button
            justify="flex-end"
            variant="outlined"
            color="primary"
            href="#outlined-buttons"
            onClick={handleSave}
          >
            Save
          </Button>
        </ListItem>
      </Dialog>
    </Box>
  );
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
