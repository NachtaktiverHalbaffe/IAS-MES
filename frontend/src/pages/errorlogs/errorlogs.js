/*
Filename: errorlogs.js
Version name: 1.0, 2021-07-10
Short description: Page to display all errors from backend

(C) 2003-2021 IAS, Universitaet Stuttgart

*/
import React, { useEffect, useLayoutEffect, useState } from "react";
import axios from "axios";
import { Box, List, ListItem, Paper, Typography } from "@material-ui/core";

import { IP_BACKEND } from "../../const";

export default function ErrorLogs() {
  // React hooks
  const [state, setState] = useState([]);
  // poll darta from backend
  useEffect(() => {
    const pollingTime = 3; // interval for polling in seconds

    const interval = setInterval(() => {
      getDataFromMes();
    }, pollingTime * 1000);

    return () => clearInterval(interval);
  });

  useLayoutEffect(() => {
    getDataFromMes();
  }, []);

  function getDataFromMes() {
    axios.get("http://" + IP_BACKEND + ":8000/api/Error/").then((res) => {
      setState(res.data);
    });
  }

  return (
    <List>
      <Paper>{createListItem(state)}</Paper>
    </List>
  );
}

// create list with data from errors
// @return:
//    items: list of errors
function createListItem(errors) {
  let items = [];
  errors.sort((a, b) => (a.id < b.id ? 1 : -1));
  for (let i = 0; i < errors.length; i++) {
    items.push(
      <ListItem width="100%" key={errors[i].id}>
        <Typography variant="body1" color="textSecondary" component="div">
          <Box fontWeight="fontWeightBold" display="inline">
            {"[" + errors[i]["timestamp"] + "]" + errors[i]["level"] + ": "}{" "}
          </Box>{" "}
          {errors[i]["category"] + ": " + errors[i]["msg"]}
        </Typography>
      </ListItem>
    );
  }
  return items;
}
