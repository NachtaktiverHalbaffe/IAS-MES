/*
Filename: stateordercard.js
Version name: 0.1, 2021-06-21
Short description: Card component for a specific working step

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import axios from "axios";
import {
  Box,
  Grid,
  Paper,
  CardActionArea,
  CardContent,
  Typography,
} from "@material-ui/core";

import EditStateOrderDialog from "../../editdialogs/editorderdialog/editorderdialog";
import { IP_BACKEND, AUTO_HIDE_DURATION } from ".../../../src/const";

export default function StateOrderCard(props) {
  let name = "";
  let description = "";
  let orderNo = 0;
  let orderPos = 0;
  let costumer = "";
  let assignedAt = "";

  const [open, setOpen] = React.useState(false);
  // statemanagment for snackbar
  const [errorState, setErrorState] = React.useState({
    snackbarOpen: false,
    msg: "",
    level: "",
  });
  const { level, msg, snackbarOpen } = errorState;
  React.useEffect(() => {
    setTimeout(() => {
      if (snackbarOpen) {
        setErrorState({
          snackbarOpen: false,
          msg: "",
          level: "",
        });
      }
    }, AUTO_HIDE_DURATION);
  });

  let data = new Map();
  if (props.description) {
    description = props.description;
    data["description"] = description;
  }
  if (props.name) {
    name = props.name;
    data["name"] = name;
  }
  if (props.orderNo) {
    orderNo = props.orderNo;
    data["orderNo"] = orderNo;
  }
  if (props.orderPos) {
    orderPos = props.orderPos;
    data["orderPos"] = orderPos;
  }
  if (props.costumer) {
    costumer = props.costumer;
    data["costumer"] = costumer;
  }
  if (props.assignedAt) {
    assignedAt = props.assignedAt;
    data["assignetAt"] = assignedAt;
  }

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = (data) => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    //update data in Mes
    axios.patch(
      "http://" +
        IP_BACKEND +
        ":8000/api/AssignedOrder/" +
        updatedData["orderNo"].toString(),
      {
        description: updatedData["description"],
        orderNo: updatedData["orderNo"],
        orderPos: updatedData["orderPos"],
        name: updatedData["name"],
      }
    );

    setErrorState({
      snackbarOpen: true,
      msg: "Sucessfully updated workingstep",
      level: "success",
    });
    return true;
  };

  return (
    <Box width={1}>
      <Paper elevation={3}>
        <CardActionArea onClick={handleClickOpen}>
          <Grid
            container
            direction="row"
            alignItems="center"
            justify="flex-start"
            width={1}
          >
            <Grid item>
              <div>&nbsp; &nbsp; &nbsp;</div>
            </Grid>
            <Grid item>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  {name}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Description:{" "}
                  </Box>{" "}
                  {description}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Order number:{" "}
                  </Box>{" "}
                  {orderNo}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Order position:{" "}
                  </Box>{" "}
                  {orderPos}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Costumer:{" "}
                  </Box>{" "}
                  {costumer}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Assigned at:{" "}
                  </Box>{" "}
                  {assignedAt}
                </Typography>
              </CardContent>
            </Grid>
          </Grid>
        </CardActionArea>
        <EditStateOrderDialog
          open={open}
          onClose={handleClose}
          data={data}
          onSave={onSave}
          title="Edit order"
        />
      </Paper>
    </Box>
  );
}
