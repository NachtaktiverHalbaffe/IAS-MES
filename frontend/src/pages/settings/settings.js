/*
Filename: settings.js
Version name: 0.1, 2021-06-29
Short description: Page to display settings

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useEffect, useLayoutEffect, useState } from "react";
import axios from "axios";
import { Box, List, ListItem, Paper, Typography } from "@material-ui/core";

import { IP_BACKEND } from "../../const";

export default function Settings() {
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

  function getDataFromMes() {
    axios.get("http://" + IP_BACKEND + ":8000/api/Setting/").then((res) => {
      if (res.data.length === 0) {
        let payload = {
          isInBridgingMode: false,
          ipAdressMES4: IP_BACKEND.toString(),
          useFleetmanager: true,
        };
        axios.post("http://" + IP_BACKEND + ":8000/api/Setting/", payload);
      } else {
        setState(res.data);
      }
    });
  }
  return (
    <Box>
      <Paper></Paper>
    </Box>
  );
}
