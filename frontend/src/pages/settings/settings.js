/*
Filename: settings.js
Version name: 0.1, 2021-06-29
Short description: Page to display settings

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React, { useEffect, useLayoutEffect, useState } from "react";
import axios from "axios";
import {
  Box,
  Button,
  Checkbox,
  CardContent,
  CardActionArea,
  Dialog,
  DialogTitle,
  Grid,
  ListItem,
  Paper,
  Typography,
} from "@material-ui/core";

import { IP_BACKEND, AUTO_HIDE_DURATION } from "../../const";
import ErrorSnackbar from "../../components/errorsnackbar/errorsnackbar";
import EditCheckBox from "../../components/edittextbox/editcheckbox";
import EditTextBox from "../../components/edittextbox/edittextbox";
import Costumer from "../../pages/settings/costumer";

export default function Settings() {
  // React hooks
  const [state, setState] = useState({
    isInBridgingMode: false,
    ipAdressMES4: "",
    useFleetmanager: false,
  });
  const [open, setOpen] = React.useState(false);
  const [errorState, setErrorState] = React.useState({
    snackbarOpen: false,
    msg: "",
    level: "",
  });
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

  const handleClickOpen = () => {
    setOpen(true);
  };

  const onSave = (updatedData) => {
    //update data in Mes
    axios.patch("http://" + IP_BACKEND + ":8000/api/Setting/1", {
      useFleetmanager: updatedData["useFleetmanager"],
    });
    return true;
  };

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
        setState(res.data[0]);
      }
    });
  }
  return (
    <Box>
      <Paper elevation={3}>
        <CardActionArea onClick={handleClickOpen}>
          <Grid
            container
            direction="row"
            alignItems="center"
            justify="space-evenly"
            width="1000px"
          >
            <Grid item>
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  Settings MES
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Use Fleetmanager to control robotino:{" "}
                  </Box>{" "}
                  <Checkbox
                    checked={state["useFleetmanager"]}
                    onChange={() => {}}
                    name="checkedB"
                    color="primary"
                  />
                </Typography>
              </CardContent>
            </Grid>
          </Grid>
        </CardActionArea>
        <EditStateWorkingPieceDialog
          open={open}
          onClose={() => {
            setOpen(false);
          }}
          onSave={onSave}
          data={state}
        />
      </Paper>
      <Costumer />
    </Box>
  );
}

function EditStateWorkingPieceDialog(props) {
  const { onClose, onSave, open, data } = props;
  const [state, setState] = React.useState(data);
  const [errorState, setErrorState] = React.useState({
    snackbarOpen: false,
    msg: "",
    level: "",
  });

  React.useEffect(() => {
    setTimeout(() => {
      if (errorState.snackbarOpen) {
        setErrorState({
          snackbarOpen: false,
          msg: "",
          level: "",
        });
      }
    }, AUTO_HIDE_DURATION);
  });

  const handleClose = () => {
    onClose();
  };

  const handleSave = () => {
    if (onSave(state)) {
      setErrorState({
        snackbarOpen: true,
        msg: "Sucessfully updated state of visualisation unit",
        level: "success",
      });
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
      <DialogTitle id="simple-dialog-title">Edit settings</DialogTitle>
      <Grid container direction="column" justify="center" alignItems="center">
        <EditCheckBox
          label="Use Fleetmanager"
          mapKey="useFleetmanager"
          initialValue={data["useFleetmanager"]}
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
      </Grid>
      <ErrorSnackbar
        level={errorState.level}
        message={errorState.msg}
        isOpen={errorState.snackbarOpen}
      />
    </Dialog>
  );
}
