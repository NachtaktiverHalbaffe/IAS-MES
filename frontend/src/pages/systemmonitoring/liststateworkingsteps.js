/*
Filename: liststateworkingsteps.js
Version name: 1.0, 2021-07-10
Short description: Component to display current orders

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useState, useEffect, useLayoutEffect } from "react";
import Box from "@material-ui/core/Box";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import axios from "axios";

//own costum components
import { IP_BACKEND } from "../../const";
import StateWorkingStepCard from "../../components/cards/workingstepcard/stateworkingstepcard";
import StateOrderCard from "../../components/cards/workingstepcard/stateordercard";
//images
import store from "../../assets/storage.png";
import assemble from "../../assets/assemble.png";
import color from "../../assets/color.png";
import imgPackage from "../../assets/package.png";
import unpackage from "../../assets/unpackage.png";
import generic from "../../assets/generic.png";

export default function ListStateWorkingSteps() {
  // React hooks
  const [order, setOrder] = useState([]);
  const [workingPlan, setWorkingPlan] = useState([]);
  const [workingSteps, setWorkingSteps] = useState([]);
  const [orderData, setOrderData] = useState([]);

  useEffect(() => {
    const pollingTime = 1.5; // interval for polling in seconds

    const interval = setInterval(async () => {
      updateData();
    }, pollingTime * 1000);
    return () => clearInterval(interval);
  });

  useLayoutEffect(() => {
    updateData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function updateData() {
    getDataFromMes();
    let orderData = [];
    // link all orders, workingplans, workingsteps and costumer together to one object
    for (let i = 0; i < order.length; i++) {
      let currentOrder = {
        order: null,
        workingPlan: null,
        workingSteps: [],
        customer: "",
      };
      currentOrder.order = order[i];
      // get customer name from mes for corresponding order
      if (currentOrder.order.customer !== null) {
        await axios
          .get(
            "http://" +
              IP_BACKEND +
              ":8000/api/Customer/" +
              currentOrder.order.customer.toString()
          )
          .then((res) => {
            currentOrder.customer =
              res.data["firstName"] + " " + res.data["lastName"];
          });
      }
      // search for workingplan object which is assigned to order
      for (let j = 0; j < workingPlan.length; j++) {
        if (workingPlan[j].workingPlanNo === order[i].assigendWorkingPlan) {
          currentOrder.workingPlan = workingPlan[j];
          break;
        }
      }
      // search for workingsteps object which is assigned to order
      for (let j = 0; j < workingSteps.length; j++) {
        let steps = workingSteps[j].sort((a, b) =>
          a["stepNo"] > b["stepNo"] ? 1 : -1
        );
        if (currentOrder.workingPlan.workingSteps[0] === steps[0].id) {
          currentOrder.workingSteps = steps;
          break;
        }
      }
      orderData.push(currentOrder);
    }
    if (orderData.length !== 0) {
      // sort orderdata by orderNo and if these match by orderPos
      orderData = orderData.sort(function (a, b) {
        if (a.order.orderNo < b.order.orderNo) return -1;
        if (a.order.orderNo > b.order.orderNo) return 1;
        if (a.order.orderPos < b.order.orderPos) return -1;
        if (a.order.orderPos > b.order.orderPos) return 1;
      });
      setOrderData(orderData);
    }
  }

  function getDataFromMes() {
    axios
      .get("http://" + IP_BACKEND + ":8000/api/AssignedOrder/")
      .then(async (res) => {
        let order = res.data;
        setOrder(order);
        let plans = [];
        for (let i = 0; i < order.length; i++) {
          if (order[i]["assigendWorkingPlan"] !== null) {
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
                  // only set workingplan if it has changed
                  setWorkingPlan(plans);
                  // get workingsteps
                  let allSteps = [];
                  for (let j = 0; j < plans.length; j++) {
                    let steps = [];
                    for (let i = 0; i < plans[j].workingSteps.length; i++) {
                      await axios
                        .get(
                          "http://" +
                            IP_BACKEND +
                            ":8000/api/WorkingStep/" +
                            plans[j].workingSteps[i].toString()
                        )
                        .then(async (res) => {
                          steps.push(res.data);
                          if (steps.length === plans[j].workingSteps.length) {
                            allSteps.push(steps);
                            if (allSteps.length === plans.length) {
                              // only set state if workingsteps have changed
                              setWorkingSteps(allSteps);
                            }
                          }
                        });
                    }
                  }
                }
              });
          }
        }
      });
  }

  return (
    <Box width={1}>
      <List>{createListItem(orderData)}</List>
    </Box>
  );
}

function createListItem(currentOrders) {
  let items = [];
  if (currentOrders.length !== 0) {
    for (let i = 0; i < currentOrders.length; i++) {
      // create card for order info
      items.push(
        <ListItem width={1} key={currentOrders[i].order.id}>
          <StateOrderCard
            name={currentOrders[i].order.name}
            description={currentOrders[i].order.description}
            orderNo={currentOrders[i].order.orderNo}
            orderPos={currentOrders[i].order.orderPos}
            assignedAt={currentOrders[i].order.assignedAt}
            customer={currentOrders[i].customer}
            id={currentOrders[i].order.id}
            customerNo={currentOrders[i].order.customer}
            assignedWorkingPiece={currentOrders[i].order.assignedWorkingPiece}
            allSteps={currentOrders[i].workingSteps}
          />
        </ListItem>
      );

      // create cards of workingsteps
      if (currentOrders[i].workingSteps.length !== 0) {
        let steps = currentOrders[i].workingSteps;
        steps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
        for (let j = 0; j < steps.length; j++) {
          let statusBits = JSON.parse(currentOrders[i].order.status);
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
          // get wright state
          let state = "";
          if (statusBits[j] === 1) {
            state = "finished";
          } else if (statusBits[j] === 0) {
            state = "pending";
          }
          const updateStatus = (index, state) => {
            if (state === "pending") {
              statusBits[index] = 0;
            } else if (state === "finished") {
              statusBits[index] = 1;
            }
            let payload = {
              status: JSON.stringify(statusBits),
            };
            axios.patch(
              "http://" +
                IP_BACKEND +
                ":8000/api/AssignedOrder/" +
                currentOrders[i].order.id.toString(),
              payload
            );
            return true;
          };
          items.push(
            <ListItem width={1} key={steps[j].id}>
              <StateWorkingStepCard
                assignedToUnit={steps[j].assignedToUnit}
                description={steps[j].description}
                name={steps[j].name}
                img={img}
                state={state}
                task={steps[j].task}
                stepNo={steps[j].stepNo}
                color={steps[j].color}
                id={steps[j].id}
                allSteps={steps}
                updateStatus={updateStatus}
                assignedToOrder={currentOrders[i].order}
              />
            </ListItem>
          );
        }
      }
    }
    return items;
  }
}
