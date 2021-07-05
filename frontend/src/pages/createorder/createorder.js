/*
Filename: createorder.js
Version name: 0.1, 2021-06-18
Short description: page for creating a order

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useEffect } from "react";
import axios from "axios";
import { Button, Box, Grid, Typography } from "@material-ui/core";

//own costum components
import EditStateOrderDialog from "../../components/editdialogs/editorderdialog/editorderdialog";
import ChooseWorkingPlanDialog from "../../components/editdialogs/chooseworkingplandialog/chooseworkingplandialog";
import StateWorkingPlanCard from "../../components/cards/workingplancard/workingplancard";
import StateOrderCard from "../../components/cards/workingstepcard/stateordercard";
import { IP_BACKEND } from "../../const";

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
      getOrderFromMes();
      getWorkingPlansFromMes();
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
          selectedWorkingPlan: createdOrder.selectedWorkingPlan,
        });
      });

    return true;
  };

  const selectWorkingPlan = (selectedPlan) => {
    let order = createdOrder.order;
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

  function getOrderFromMes(){
    axios.get(
      "http://" +
        IP_BACKEND +
        ":8000/api/AssignedOrder/" +
        createdOrder.order["id"].toString()).then((res)=>{
          setCreatedOrder({
          order: res.data,
          selectedWorkingPlan: createdOrder.selectedWorkingPlan,
           });
        });
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
      <Grid container justify="center" alignItems="center" direction="column">
        {createListItem(createdOrder.order, createdOrder.selectedWorkingPlan)}
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
            color="secondary"
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

function createListItem(order, workingPlan) {
  let items = [];
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
          assignedWorkingPiece= {order.assignedWorkingPiece}
          id = {order.id}
        />
      </Grid>
    );
  }

  if (workingPlan["workingPlanNo"] !== 0) {
    items.push(
      <Grid item xs={12}>
        <Grid item>
          <div>&nbsp; &nbsp; &nbsp;</div>
        </Grid>
        <StateWorkingPlanCard
          name={workingPlan["name"]}
          description={workingPlan["description"]}
          workingPlanNo={workingPlan["workingPlanNo"]}
          workingSteps={workingPlan["workingSteps"]}
        />
      </Grid>
    );
  }

  return items;
}
