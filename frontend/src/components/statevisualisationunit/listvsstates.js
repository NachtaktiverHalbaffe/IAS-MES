import React, { useState, useEffect } from "react";
import Box from "@material-ui/core/Box";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import { GridList } from "@material-ui/core";
import axios from "axios";

import StateVSCard from "./statevscard";
import visualisationUnit from "../../assets/visualisationunit.png";

export default function ListVSStates() {
  //const IP_BACKEND = "127.0.0.1";
  const IP_BACKEND = "192.168.178.30";
  //const IP_BACKEND ="129.69.102.129";

  // React hooks
  const [state, setState] = useState([]);
  useEffect(() => {
    const pollingTime = 1.5; // interval for polling in seconds

    const interval = setInterval(() => {
      getDataFromMes();
    }, pollingTime * 1000);

    return () => clearInterval(interval);
  }, []);

  function createListItem(statesVS) {
    let items = [];
    statesVS.sort((a, b) => (a.boundToRessource > b.boundToRessource ? 1 : -1));
    for (let i = 0; i < statesVS.length; i++) {
      // get image depending on resourceId
      let img = visualisationUnit;
      items.push(
        <ListItem width={1}>
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
      <GridList cellHeight={200} cols={2} spacing={20}>
        {createListItem(state)}
      </GridList>
    </Box>
  );
}
