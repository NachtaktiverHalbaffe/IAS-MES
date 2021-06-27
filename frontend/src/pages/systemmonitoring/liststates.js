import React, { useState, useEffect, useLayoutEffect } from "react";
import { GridList, ListItem } from "@material-ui/core";
import axios from "axios";

import { IP_BACKEND } from "../../const";
import StatePLCCard from "../../components/cards/stateplccard/stateplccard";
import branch from "../../assets/branch.png";
import storage from "../../assets/storage.png";
import robotino from "../../assets/robotino.png";

export default function ListStates() {
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

  function createListItem(statesPLC) {
    let items = [];
    statesPLC.sort((a, b) => (a.id > b.id ? 1 : -1));
    for (let i = 0; i < statesPLC.length; i++) {
      // get image depending on resourceId
      let img = null;
      if (statesPLC[i].id === 1) {
        img = storage;
      } else if (statesPLC[i].id < 7) {
        img = branch;
      } else {
        img = robotino;
      }

      items.push(
        <ListItem width="100%">
          <StatePLCCard
            name={statesPLC[i].name}
            mode={statesPLC[i].mode}
            image={img}
            state={statesPLC[i].state}
            resourceId={statesPLC[i].id}
          />
        </ListItem>
      );
    }
    return items;
  }

  function getDataFromMes() {
    axios.get("http://" + IP_BACKEND + ":8000/api/StatePLC/").then((res) => {
      setState(res.data);
    });
  }

  return (
    <GridList cellHeight={170} cols={3} spacing={15}>
      {createListItem(state)}
    </GridList>
  );
}
