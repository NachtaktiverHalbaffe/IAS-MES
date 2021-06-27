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

export default function StateWorkingPlanCard(props) {
  let name = "";
  let description = "";
  let workingPlanNo = 0;

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
  if (props.workingPlanNo) {
    workingPlanNo = props.workingPlanNo;
    data["workingPlanNo"] = workingPlanNo;
  }

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = (data) => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    //validate data
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
        msg: "Description too long. Max length: 30",
        level: "warning",
      });
      return false;
    }
    if (
      isNaN(updatedData["workingPlanNo"]) ||
      updatedData["workingPlanNo"] < 1
    ) {
      setErrorState({
        snackbarOpen: true,
        msg: "Workingplan isnt a positive number",
        level: "warning",
      });
      return false;
    }
    let payload = {};
    if (updatedData["description"] !== "") {
      payload = {
        name: updatedData["name"],
        description: updatedData["description"],
        workingPlanNo: parseInt(updatedData["workingPlanNo"]),
        workingSteps: [],
      };
    } else {
      payload = {
        name: updatedData["name"],
        workingPlanNo: parseInt(updatedData["workingPlanNo"]),
        workingSteps: [],
      };
    }
    axios.patch("http://" + IP_BACKEND + ":8000/api/WorkingPlan/", payload);
    setErrorState({
      snackbarOpen: true,
      msg: "Successfully edited workingplan",
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
                    Workingplan number:{" "}
                  </Box>{" "}
                  {workingPlanNo}
                </Typography>
              </CardContent>
            </Grid>
          </Grid>
        </CardActionArea>
        <EditStateWorkingPlanDialog
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

function EditStateWorkingPlanDialog(props) {
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
        helperText="Name of the workingplan"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Description"
        mapKey="description"
        initialValue={data["description"]}
        helperText="Description of the workingplan(optional)"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Workingplan number"
        mapKey="workingPlanNo"
        initialValue={data["workingPlanNo"]}
        helperText="Number of the workingplan. Identifies the workingplan"
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
