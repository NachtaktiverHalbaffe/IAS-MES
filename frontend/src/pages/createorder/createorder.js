/*
Filename: createorder.js
Version name: 0.1, 2021-06-18
Short description: page for creating a order

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useEffect } from "react";
import axios from "axios";
import {
  Button,
  Box,
  List,
  ListItem,
  Grid,
  Typography,
} from "@material-ui/core";

//own costum components
import EditStateOrderDialog from "../../components/editdialogs/editorderdialog/editorderdialog";
import ChooseWorkingPlanDialog from "../../components/editdialogs/chooseworkingplandialog/chooseworkingplandialog";
import StateWorkingStepCard from "../../components/cards/workingstepcard/stateworkingstepcard";
import StateWorkingPlanCard from "../../components/cards/workingplancard/workingplancard";
import StateOrderCard from "../../components/cards/workingstepcard/stateordercard";
import { IP_BACKEND } from "../../const";

//images
import store from "../../assets/storage.png";
import assemble from "../../assets/assemble.png";
import color from "../../assets/color.png";
import imgPackage from "../../assets/package.png";
import unpackage from "../../assets/unpackage.png";
import generic from "../../assets/generic.png";

export default function CreateOrder() {
  const [state, setState] = React.useState({
    workingPlans: [],
    workingSteps: [],
  });
  const [createdOrder, setCreatedOrder] = React.useState({
    order: {
      id: 0,
      name: "",
      description: "",
      assigendWorkingPlan: 0,
      assignedWorkingPiece: 0,
      orderNo: 0,
      orderPos: 0,
      mainOrderPos: 0,
    },
    selectedWorkingPlan: {
      name: "",
      description: "",
      workingPlanNo: 0,
      workingSteps: [],
    },
  });
  const [open, setOpen] = React.useState(true);
  const [openChooseDialog, setOpenChooseDialog] = React.useState(false);

  useEffect(() => {
    const pollingTime = 1; // interval for polling in seconds

    const interval = setInterval(async () => {
      // set dialog of creating an workinplan to open if not created
      if (createdOrder.order["orderNo"] === 0) {
        setOpen(true);
      }
      getWorkingPlansFromMes();
      if (state.workingSteps.length !== 0) {
        getWorkingStepsFromMes();
      }
    }, pollingTime * 1000);
    return () => clearInterval(interval);
  });

  const handleClose = () => {
    setOpen(false);
  };

  const createOrder = (data) => {
    let payload = {
      name: data["name"],
      orderNo: data["orderNo"],
      orderPos: data["orderPos"],
    };
    if (data["description"] !== "") {
      payload["description"] = data["description"];
    }
    axios
      .post("http://" + IP_BACKEND + ":8000/api/AssignedOrder/", payload)
      .then((res) => {
        setCreatedOrder({
          order: res.data,
          selectedWorkingPlan: createdOrder.workingSteps,
        });
      });

    return true;
  };

  const selectWorkingPlan = (selectedPlan) => {
    let order = createdOrder.order;
    order["assigendWorkingPlan"] = selectedPlan["workingPlanNo"];
    setCreatedOrder({
      order: order,
      selectedWorkingPlan: selectedPlan,
    });
    let payload = {
      assigendWorkingPlan: selectedPlan["workingPlanNo"],
    };
    axios.patch(
      "http://" +
        IP_BACKEND +
        ":8000/api/AssignedOrder/" +
        order["id"].toString(),
      payload
    );
    setOpenChooseDialog(false);
    return true;
  };

  function getWorkingPlansFromMes() {
    axios
      .get("http://" + IP_BACKEND + ":8000/api/WorkingPlan/")
      .then(async (res) => {
        let plans = res.data;
        await setState({
          workingPlans: plans,
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
    <Box justify="center" alignItems="center">
      <EditStateOrderDialog
        data={{
          name: "",
          description: "",
          workingPlanNo: 0,
        }}
        onSave={createOrder}
        open={open}
        onClose={handleClose}
        title="Create Order"
      />
      <Grid
        container
        spacing={0}
        justify="center"
        alignItems="center"
        direction="column"
      >
        {createListItem(
          createdOrder.order,
          createdOrder.workingPlan,
          createdOrder.workingSteps
        )}
        <Grid item>
          <div>&nbsp; &nbsp; &nbsp;</div>
        </Grid>
        <Typography gutterBottom variant="h5" component="h2">
          Create order (changes gets autosaved)
        </Typography>
        <Grid item>
          <div>&nbsp; &nbsp; &nbsp;</div>
        </Grid>
        <Grid item>
          <Button
            justify="flex-end"
            variant="outlined"
            color="primary"
            href="#outlined-buttons"
            onClick={() => {
              setOpenChooseDialog(true);
            }}
          >
            Select workingplan
          </Button>
        </Grid>
        <ChooseWorkingPlanDialog
          open={openChooseDialog}
          selectWorkingPlan={selectWorkingPlan}
          title="Choose workingplan to execute"
          onClose={() => {
            setOpenChooseDialog(false);
          }}
          workingPlans={state.workingPlans}
        />
      </Grid>
    </Box>
  );
}

function createListItem(order, workingPlan, workingSteps) {
  let items = [];
  let steps = workingSteps;
  if (order["orderNo"] !== 0) {
    items.push(
      <Grid item xs={12}>
        <StateOrderCard
          name={order.name}
          description={order.description}
          orderNo={order.orderNo}
          orderPos={order.orderPos}
          assignedAt={order.assignedAt}
          costumer=""
        />
      </Grid>
    );
  }

  //   if (steps.length > 1) {
  //     steps = steps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
  //   }
  //   for (let j = 0; j < steps.length; j++) {
  //     // get right image
  //     let img = null;
  //     if (steps[j].task === "unstore" || steps[j].task === "store") {
  //       img = store;
  //     } else if (steps[j].task === "assemble") {
  //       img = assemble;
  //     } else if (steps[j].task === "color") {
  //       img = color;
  //     } else if (steps[j].task === "generic") {
  //       img = generic;
  //     } else if (steps[j].task === "package") {
  //       img = imgPackage;
  //     } else if (steps[j].task === "unpackage") {
  //       img = unpackage;
  //     }
  //     // get wright order
  //     items.push(
  //       <ListItem width={1} key={steps[j].id}>
  //         <StateWorkingStepCard
  //           assignedToUnit={steps[j].assignedToUnit}
  //           description={steps[j].description}
  //           name={steps[j].name}
  //           img={img}
  //           state="pending"
  //           task={steps[j].task}
  //           stepNo={steps[j].stepNo}
  //           color={steps[j].color}
  //           id={steps[j].id}
  //         />
  //       </ListItem>
  //     );
  //   }

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
