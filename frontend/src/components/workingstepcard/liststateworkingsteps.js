/*
Filename: liststateworkingsteps.js
Version name: 0.1, 2021-05-14
Short description: Component to display current orders. gets data from mes and creates visual elements

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useState, useEffect, useLayoutEffect } from "react";
import Box from "@material-ui/core/Box";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import axios from "axios";

//own costum components
import StateWorkingStepCard from "./stateworkingstepcard";
import StateOrderCard from "./stateordercard";
//images
import store from "../../assets/storage.png";
import assemble from "../../assets/assemble.png";
import color from "../../assets/color.png";
import imgPackage from "../../assets/package.png";
import unpackage from "../../assets/unpackage.png";
import generic from "../../assets/generic.png";

export default function ListStateWorkingSteps() {
  //const IP_BACKEND = "127.0.0.1";
  const IP_BACKEND = "192.168.178.30";
  //const IP_BACKEND ="129.69.102.129";

  // React hooks
  const [order, setOrder] = useState([]);
  const [workingPlan, setWorkingPlan] = useState([]);
  const [workingSteps, setWorkingSteps] = useState([]);

  useEffect(() => {
    const pollingTime = 1; // interval for polling in seconds

    const interval = setInterval(async () => {
      getOrderFromMes();
      getWorkingPlanFromMes();
      getWorkingStepsFromMes();
    }, pollingTime * 1000);
    return () => clearInterval(interval);
  });

  function createListItem(currentOrders, wp, wssteps, costumer) {
    let items = [];
    for (let i = 0; i < currentOrders.length; i++) {
      // create card for order info
      items.push(
        <ListItem width={1}>
          <StateOrderCard
            name={currentOrders[i].name}
            description={currentOrders[i].description}
            orderNo={currentOrders[i].orderNo}
            orderPos={currentOrders[i].orderPos}
            assignedAt={currentOrders[i].assignedAt}
            costumer={costumer}
          />
        </ListItem>
      );

      // create cards of workingsteps
      if (wssteps.length != 0) {
        let steps = wssteps[i];
        steps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
        for (let j = 0; j < steps.length; j++) {
          let statusBits = JSON.parse(currentOrders[i].status);
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
          let state = "";
          if (statusBits[j] === 1) {
            state = "finished";
          } else if (statusBits[j] === 0) {
            state = "pending";
          }

          items.push(
            <ListItem width={1}>
              <StateWorkingStepCard
                assignedToUnit={steps[j].assignedToUnit}
                description={steps[j].description}
                name={steps[j].name}
                img={img}
                state={state}
                task={steps[j].task}
                stepNo={steps[j].stepNo}
              />
            </ListItem>
          );
        }
      }
    }
    return items;
  }

  function getOrderFromMes() {
    axios
      .get("http://" + IP_BACKEND + ":8000/api/AssignedOrder/")
      .then(async (res) => {
        await setOrder(res.data);
      });
  }

  async function getWorkingPlanFromMes() {
    let plans = [];
    for (let i = 0; i < order.length; i++) {
      axios
        .get(
          "http://" +
            IP_BACKEND +
            ":8000/api/WorkingPlan/" +
            order[i].assigendWorkingPlan.toString()
        )
        .then(async (res) => {
          plans.push(res.data);
          if (plans.length === order.length) {
            let oldPlan = await workingPlan;
            // only set workingplan if it has changed
            if (!mCompareWorkingPlans(oldPlan, plans)) {
              await setWorkingPlan(plans);
            }
          }
        });
    }
  }

  function getWorkingStepsFromMes() {
    let steps = [];
    let allSteps = [];
    for (let j = 0; j < workingPlan.length; j++) {
      for (let i = 0; i < workingPlan[j].workingSteps.length; i++) {
        axios
          .get(
            "http://" +
              IP_BACKEND +
              ":8000/api/WorkingStep/" +
              workingPlan[j].workingSteps[i].toString()
          )
          .then(async (res) => {
            steps.push(res.data);
            if (steps.length === workingPlan[j].workingSteps.length) {
              allSteps.push(steps);
              steps = [];
              if (allSteps.length === workingPlan.length) {
                let oldSteps = workingSteps;
                // only set state if workingsteps have changed
                if (!mCompareWorkingSteps(oldSteps, allSteps)) {
                  setWorkingSteps(allSteps);
                }
              }
            }
          });
      }
    }
  }

  return (
    <Box width={1}>
      <List>
        {createListItem(order, workingPlan, workingSteps, "Max Mustermann")}
      </List>
    </Box>
  );
}

// compares if two states of Workingplans are equal. Returns true if equal and vise versa
function mCompareWorkingPlans(oldPlan, newPlan) {
  // check lengths
  if (oldPlan.length != newPlan.length) {
    return false;
  }
  for (let i = 0; i < oldPlan.length; i++) {
    if (oldPlan[i].length != newPlan[i].length) {
      return false;
    } else if (
      oldPlan[i].workingSteps.length === newPlan[i].workingSteps.length
    ) {
      let old = oldPlan[i].workingSteps;
      old.sort((a, b) => (a > b ? 1 : -1));
      let newP = newPlan[i].workingSteps;
      newP.sort((a, b) => (a > b ? 1 : -1));
      for (let j = 0; j < old.length; j++) {
        if (old[j] != newP[j]) {
          return false;
        }
      }
    }
  }
  return true;
}

// compares if two states of Workingsteps are equal. Returns true if equal and vise versa
function mCompareWorkingSteps(oldSteps, newSteps) {
  // check lengths
  if (oldSteps.length != newSteps.length) {
    return false;
  }
  // check workingsteps
  for (let i = 0; i < oldSteps.length; i++) {
    if (oldSteps[i].length != newSteps[i].length) {
      return false;
    } else if (oldSteps[i].length === newSteps[i].length) {
      let old = oldSteps[i];
      old.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
      let newP = newSteps[i];
      newP.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
      for (let j = 0; j < old.length; j++) {
        if (old[j].task != newP[j].task) {
          return false;
        }
        if (old[j].color != newP[j].color) {
          return false;
        }
        if (old[j].assignedToUnit != newP[j].assignedToUnit) {
          return false;
        }
        if (old[j].name != newP[j].name) {
          return false;
        }
        if (old[j].description != newP[j].description) {
          return false;
        }
      }
    }
  }
  return true;
}
