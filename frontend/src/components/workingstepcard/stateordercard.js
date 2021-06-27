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
  DialogTitle,
  ListItem,
  Button,
  Dialog,
  Typography,
} from "@material-ui/core";

import EditTextBox from "../edittextbox/edittextbox";
import ErrorSnackbar from "../errorsnackbar/errorsnackbar";
import { IP_BACKEND, AUTO_HIDE_DURATION } from "../../const";

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
    //validate data
    if (isNaN(updatedData["orderNo"]) || updatedData["orderNo"] < 1) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid ordernumber. Must be a positive number and not 0",
        level: "warning",
      });
      return false;
    }
    if (isNaN(updatedData["orderPos"]) || updatedData["orderpos"] < 1) {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid order position. Must be a positive number and not 0",
        level: "warning",
      });
      return false;
    }
    if (updatedData["name"].length > 30) {
      setErrorState({
        snackbarOpen: true,
        msg: "Name too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    if (updatedData["description"].length > 200) {
      setErrorState({
        snackbarOpen: true,
        msg: "Description too long. Max length: 200",
        level: "warning",
      });
      return false;
    }

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
        />
      </Paper>
      <ErrorSnackbar level={level} message={msg} isOpen={snackbarOpen} />
    </Box>
  );
}

function EditStateOrderDialog(props) {
  const { onClose, onSave, open, data } = props;
  const [state, setState] = React.useState(data);

  const handleClose = () => {
    onClose();
  };

  const handleSave = () => {
    if (onSave(state)) {
      handleClose();
    }
  };

  const onEdit = (key, value) => {
    let newState = state;
    newState[key] = value;
    setState(newState);
  };

  return (
    <Dialog
      onClose={handleClose}
      aria-labelledby="simple-dialog-title"
      open={open}
    >
      <DialogTitle id="simple-dialog-title">Edit order</DialogTitle>
      <EditTextBox
        label="Name"
        mapKey="name"
        initialValue={data["name"]}
        helperText="Name of the order"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Description"
        mapKey="description"
        initialValue={data["description"]}
        helperText="Description of the order (optional)"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Order number"
        mapKey="orderNo"
        initialValue={data["orderNo"]}
        helperText="Order number of the order"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Order position"
        mapKey="orderPos"
        initialValue={data["orderPos"]}
        helperText="Position of an order within the order itself if an order contains multiple orders"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Costumer"
        mapKey="costumer"
        initialValue={data["costumer"]}
        helperText="Name of the costumer who assigned the order(optional). Only change if new costumer is already created as an costumer"
        onEdit={onEdit}
      />
      <ListItem justify="flex-end">
        <Button
          justify="flex-end"
          variant="outlined"
          color="primary"
          href="#outlined-buttons"
          onClick={handleSave}
        >
          Save
        </Button>
      </ListItem>
    </Dialog>
  );
}
