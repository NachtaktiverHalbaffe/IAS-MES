/*
Filename: listvsstates.js
Version name: 1.0, 2021-07-10
Short description: list with cards of the states of all visualisation units

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useState, useEffect, useLayoutEffect } from "react";
import axios from "axios";
import { Box, GridList, ListItem } from "@material-ui/core";

import { IP_BACKEND } from "../../const";
import StateVSCard from "../../components/cards/statevisualisationunit/statevscard";
import visualisationUnit from "../../assets/visualisationunit.png";

export default function ListVSStates() {
  // React hooks
  const [state, setState] = useState([]);
  useEffect(() => {
    const pollingTime = 1.5; // interval for polling in seconds

    const interval = setInterval(() => {
      getDataFromMes();
    }, pollingTime * 1000);

    return () => clearInterval(interval);
  }, []);
  useLayoutEffect(() => {
    getDataFromMes();
  }, []);

  function createListItem(statesVS) {
    let items = [];
    statesVS.sort((a, b) => (a.boundToRessource > b.boundToRessource ? 1 : -1));
    for (let i = 0; i < statesVS.length; i++) {
      // get image depending on resourceId
      let img = visualisationUnit;
      items.push(
        <ListItem width={1} key={statesVS[i].boundToRessource}>
          <StateVSCard
            boundToRessource={statesVS[i].boundToRessource}
            ipadress={statesVS[i].ipAdress}
            img={img}
            state={statesVS[i].state}
            task={statesVS[i].assignedTask}
            baseLevelHeight={statesVS[i].baseLevelHeight}
          />
        </ListItem>
      );
    }
    return items;
  }

  function getDataFromMes() {
    axios
      .get("http://" + IP_BACKEND + ":8000/api/StateVisualisationUnit/")
      .then((res) => {
        setState(res.data);
      });
  }

  return (
    <Box width={1}>
      <GridList cellHeight={180} cols={2} spacing={15}>
        {createListItem(state)}
      </GridList>
    </Box>
  );
}
