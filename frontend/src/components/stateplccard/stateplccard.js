/*
Filename: stateplccard.js
Version name: 0.1, 2021-06-19
Short description: Card component for a specific state of plc

(C) 2003-2021 IAS, Universitaet Stuttgart

*/
import axios from "axios";
import React from "react";
import Box from "@material-ui/core/Box";
import {
  Grid,
  Paper,
  ListItem,
  Dialog,
  DialogTitle,
  CardContent,
  CardActionArea,
  Button,
  Typography,
} from "@material-ui/core";

import EditTextBox from "../edittextbox/edittextbox";
import ErrorSnackbar from "../errorsnackbar/errorsnackbar";
import { IP_BACKEND, AUTO_HIDE_DURATION } from "../../const";

export default function StatePLCCard(props) {
  let name = "";
  let mode = "";
  let state = "";
  let image = "";
  let resourceId = "";
  let data = new Map();

  const [open, setOpen] = React.useState(false);
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

  if (props.name) {
    name = props.name;
    data["name"] = name;
  }
  if (props.image) {
    image = props.image;
    data["image"] = image;
  }
  if (props.state) {
    state = props.state;
    data["state"] = state;
  }
  if (props.mode) {
    mode = props.mode;
    data["mode"] = mode;
  }
  if (props.resourceId) {
    resourceId = props.resourceId;
    data["resourceId"] = resourceId;
  }

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    //validate input data
    if (updatedData["state"] !== "idle" && updatedData["state"] !== "busy") {
      setErrorState({
        snackbarOpen: true,
        msg: "Invalid state. Possible states: busy and idle",
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
    // validate other data against error
    if (
      updatedData["resourceId"] < 1 ||
      isNaN(updatedData["resourceId"]) ||
      updatedData["resourceId"] > 10
    ) {
      setErrorState({
        snackbarOpen: true,
        msg: "Internal error: Invalid resourceId.",
        level: "warning",
      });
      return false;
    }

    //update data in Mes
    axios.patch(
      "http://" +
        IP_BACKEND +
        ":8000/api/StatePLC/" +
        updatedData["resourceId"].toString(),
      {
        state: updatedData["state"],
        name: updatedData["name"],
      }
    );
    setErrorState({
      snackbarOpen: true,
      msg: "Successfully updated state of resource",
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
            width="1000px"
          >
            <Grid item>
              <div>&nbsp; &nbsp; &nbsp;</div>
            </Grid>
            <Grid item>
              <img
                src={image}
                alt="Image of resource"
                width="100px"
                height="100px"
                alignItems="center"
                margin="10px"
              />
            </Grid>
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
                    State:{" "}
                  </Box>{" "}
                  {state}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    ResourceId:{" "}
                  </Box>{" "}
                  {resourceId}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Mode:{" "}
                  </Box>{" "}
                  {mode}
                </Typography>
              </CardContent>
            </Grid>
          </Grid>
        </CardActionArea>
        <EditStatePLCDialog
          open={open}
          onClose={handleClose}
          onSave={onSave}
          data={data}
        />
      </Paper>
      <ErrorSnackbar level={level} message={msg} isOpen={snackbarOpen} />
    </Box>
  );
}

function EditStatePLCDialog(props) {
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
      justify="center"
    >
      <DialogTitle id="simple-dialog-title">Edit State of Resource</DialogTitle>
      <EditTextBox
        label="Name"
        mapKey="name"
        initialValue={data["name"]}
        helperText="Name of the resource"
        onEdit={onEdit}
      />
      <EditTextBox
        label="State"
        mapKey="state"
        initialValue={data["state"]}
        helperText="State of the resource. Don't change if not necessary"
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
