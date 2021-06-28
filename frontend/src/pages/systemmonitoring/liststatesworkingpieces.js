/*
Filename: liststateworkingpieces.js
Version name: 0.1, 2021-06-28
Short description: top level card for löisting workingpieces

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useState, useEffect, useLayoutEffect } from "react";
import { GridList, ListItem } from "@material-ui/core";
import axios from "axios";

import { IP_BACKEND } from "../../const";
import StateWorkingPieceCard from "../../components/cards/stateworkingpiececard/stateworkingpiececard";

export default function ListStateWorkingPieces() {
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

  function createListItem(statesWorkingPieces) {
    let items = [];
    statesWorkingPieces.sort((a, b) => (a.id > b.id ? 1 : -1));
    for (let i = 0; i < statesWorkingPieces.length; i++) {
      items.push(
        <ListItem width="100%">
          <StateWorkingPieceCard
            id={statesWorkingPieces[i]["id"]}
            location={statesWorkingPieces[i]["location"]}
            partNo={statesWorkingPieces[i]["partNo"]}
            carrierId={statesWorkingPieces[i]["carrierId"]}
            storageLocation={statesWorkingPieces[i]["storageLocation"]}
            color={statesWorkingPieces[i]["color"]}
            isAssembled={statesWorkingPieces[i]["isAssembled"]}
            isPackaged={statesWorkingPieces[i]["isPackaged"]}
            model={statesWorkingPieces[i]["model"]}
          />
        </ListItem>
      );
    }
    return items;
  }

  function getDataFromMes() {
    axios
      .get("http://" + IP_BACKEND + ":8000/api/StateWorkingPiece/")
      .then((res) => {
        if (res.data.length !== 0) {
          setState(res.data);
        } else {
          for (let i = 0; i < 30; i++) {
            let payload = {
              storageLocation: i + 1,
            };
            console.log(payload);
            axios.post(
              "http://" + IP_BACKEND + ":8000/api/StateWorkingPiece/",
              payload
            );
          }
        }
      });
  }

  return (
    <GridList cellHeight={270} cols={3} spacing={30}>
      {createListItem(state)}
    </GridList>
  );
}
