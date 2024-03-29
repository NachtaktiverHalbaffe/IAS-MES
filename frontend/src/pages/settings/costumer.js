/*
Filename: customer.js
Version name: 1.0, 2021-07-10
Short description: Card component for customers

(C) 2003-2021 IAS, Universitaet Stuttgart

*/
import axios from "axios";
import React, { useEffect } from "react";
import {
  Box,
  Grid,
  Paper,
  List,
  ListItem,
  Dialog,
  DialogTitle,
  CardContent,
  CardActionArea,
  Fab,
  Button,
  Typography,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/core/styles";
import AddIcon from "@material-ui/icons/Add";

import EditTextBox from "../../components/edittextbox/edittextbox";
import ErrorSnackbar from "../../components/errorsnackbar/errorsnackbar";
import { IP_BACKEND, AUTO_HIDE_DURATION } from ".../../../src/const";

const useStyles = makeStyles((theme) => ({
  root: {
    backgroundColor: theme.palette.background.paper,
    width: 500,
    position: "relative",
    minHeight: 200,
  },
  fab: {
    position: "absolute",
    bottom: theme.spacing(2),
    right: theme.spacing(2),
  },
}));

export default function Customer() {
  const classes = useStyles();
  const [state, setState] = React.useState([]);

  useEffect(() => {
    const pollingTime = 1; // interval for polling in seconds

    const interval = setInterval(() => {
      getDataFromMes();
    }, pollingTime * 1000);
    return () => clearInterval(interval);
  });

  const [wsopen, setWSOpen] = React.useState(false);
  // states stuff for opening and closing dialogs
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

  const handleWSClose = () => {
    setWSOpen(false);
  };

  const createCustomer = (data) => {
    if (data["customerNo"] < 1 || isNaN(data["customerNo"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Costumer number must be greater than 0 and must be a integer",
        level: "warning",
      });
      return false;
    }
    if (data["firstName"] === "") {
      setErrorState({
        snackbarOpen: true,
        msg: "A first name is needed",
        level: "warning",
      });
      return false;
    }
    if (data["lastName"] === "") {
      setErrorState({
        snackbarOpen: true,
        msg: "A last name is needed",
        level: "warning",
      });
      return false;
    }
    let payload = {
      customerNo: data["customerNo"],
      firstName: data["firstName"],
      lastName: data["lastName"],
    };
    if (data["adress"] !== "") {
      payload["adress"] = data["adress"];
    }
    if (data["phone"] !== "") {
      payload["phone"] = data["phone"];
    }
    if (data["eMail"] !== "") {
      payload["eMail"] = data["eMail"];
    }
    if (data["company"] !== "") {
      payload["company"] = data["company"];
    }

    axios.post("http://" + IP_BACKEND + ":8000/api/Costumer/", payload);
    setErrorState({
      snackbarOpen: true,
      msg: "Successfully created customer",
      level: "success",
    });
    return true;
  };

  function getDataFromMes() {
    axios
      .get("http://" + IP_BACKEND + ":8000/api/Customer/")
      .then(async (res) => {
        setState(res.data);
      });
  }

  const fab = [
    {
      color: "primary",
      className: classes.fab,
      icon: <AddIcon />,
      label: "Add",
    },
  ];

  return (
    <Box>
      <Grid
        container
        justify="space-evenly"
        alignItems="center"
        direction="column"
      >
        <div>&nbsp; &nbsp; &nbsp;</div>
        <Typography gutterBottom variant="h5" component="h2">
          Customers
        </Typography>
        <List width={1}>{createListItem(state)}</List>
        <Grid item>
          <Fab
            color="secondary"
            aria-label="add"
            className={fab.className}
            onClick={() => {
              setWSOpen(true);
            }}
          >
            <AddIcon />
          </Fab>
          <div>&nbsp; &nbsp; &nbsp;</div>
        </Grid>
      </Grid>
      <EditCostumerDialog
        data={{
          customerNo: 0,
          firstName: "",
          lastName: "",
          adress: "",
          phone: "",
          eMail: "",
          company: "",
        }}
        onSave={createCustomer}
        open={wsopen}
        onClose={handleWSClose}
      />
      <ErrorSnackbar
        level={errorState.level}
        message={errorState.msg}
        isOpen={errorState.snackbarOpen}
      />
    </Box>
  );
}

function createListItem(customers) {
  let items = [];
  for (let j = 0; j < customers.length; j++) {
    items.push(
      <ListItem>
        <CostumerCard
          customerNo={customers[j].customerNo}
          firstName={customers[j].firstName}
          lastName={customers[j].lastName}
          adress={customers[j].adress}
          phone={customers[j].phone}
          eMail={customers[j].eMail}
          company={customers[j].company}
        />
      </ListItem>
    );
  }

  return items;
}

function CostumerCard(props) {
  let customerNo = 0;
  let firstName = "";
  let lastName = "";
  let adress = "";
  let phone = "";
  let eMail = "";
  let company = "";
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

  if (props.customerNo) {
    customerNo = props.customerNo;
    data["customerNo"] = customerNo;
  }
  if (props.firstName) {
    firstName = props.firstName;
    data["firstName"] = firstName;
  }
  if (props.lastName) {
    lastName = props.lastName;
    data["lastName"] = lastName;
  }
  if (props.adress) {
    adress = props.adress;
    data["adress"] = adress;
  }
  if (props.phone) {
    phone = props.phone;
    data["phone"] = phone;
  }
  if (props.eMail) {
    eMail = props.eMail;
    data["eMail"] = eMail;
  }
  if (props.company) {
    company = props.company;
    data["company"] = company;
  }

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const onSave = (updatedData) => {
    if (updatedData["customerNo"] < 1 || isNaN(updatedData["customerNo"])) {
      setErrorState({
        snackbarOpen: true,
        msg: "Costumer number must be greater than 0 and must be a integer",
        level: "warning",
      });
      return false;
    }
    if (updatedData["firstName"] === "") {
      setErrorState({
        snackbarOpen: true,
        msg: "A first name is needed",
        level: "warning",
      });
      return false;
    }
    if (updatedData["lastName"] === "") {
      setErrorState({
        snackbarOpen: true,
        msg: "A last name is needed",
        level: "warning",
      });
      return false;
    }

    //update data in Mes
    axios.patch(
      "http://" +
        IP_BACKEND +
        ":8000/api/Costumer/" +
        updatedData["customerNo"].toString(),
      {
        customerNo: updatedData["customerNo"],
        firstName: updatedData["firstName"],
        lastName: updatedData["lastName"],
        adress: updatedData["adress"],
        phone: updatedData["phone"],
        eMail: updatedData["eMail"],
        company: updatedData["company"],
      }
    );
    setErrorState({
      snackbarOpen: true,
      msg: "Successfully updated state of resource",
      level: "success",
    });
    return true;
  };

  const onDelete = (customerToDelete) => {
    axios.delete(
      "http://" +
        IP_BACKEND +
        ":8000/api/Costumer/" +
        customerToDelete["customerNo"].toString()
    );
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
              <CardContent>
                <Typography gutterBottom variant="h5" component="h2">
                  {firstName + " " + lastName}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Costumer number:{" "}
                  </Box>{" "}
                  {customerNo}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Adress:{" "}
                  </Box>{" "}
                  {adress}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Phone:{" "}
                  </Box>{" "}
                  {phone}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    E-Mail:{" "}
                  </Box>{" "}
                  {eMail}
                </Typography>
                <Typography
                  variant="body1"
                  color="textSecondary"
                  component="div"
                >
                  <Box fontWeight="fontWeightBold" display="inline">
                    Company:{" "}
                  </Box>{" "}
                  {company}
                </Typography>
              </CardContent>
            </Grid>
          </Grid>
        </CardActionArea>
        <EditCostumerDialog
          open={open}
          onClose={handleClose}
          onSave={onSave}
          onDelete={onDelete}
          data={data}
        />
      </Paper>
      <ErrorSnackbar level={level} message={msg} isOpen={snackbarOpen} />
    </Box>
  );

  // render card for robotinos
}

function EditCostumerDialog(props) {
  const { onClose, onSave, onDelete, open, data } = props;
  const [state, setState] = React.useState(data);

  const handleClose = () => {
    onClose();
  };

  const handleSave = () => {
    if (onSave(state)) {
      handleClose();
    }
  };

  const handleDelete = () => {
    if (onDelete(state)) {
      handleClose();
      return true;
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
      <DialogTitle id="simple-dialog-title">Edit Costumer</DialogTitle>
      <EditTextBox
        label="Costumer number"
        mapKey="customerNo"
        initialValue={data["customerNo"]}
        helperText="Costumer number of customer. Identifies the customer"
        onEdit={onEdit}
      />
      <EditTextBox
        label="First name"
        mapKey="firstName"
        initialValue={data["firstName"]}
        helperText="First name of customer"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Last name"
        mapKey="lastName"
        initialValue={data["lastName"]}
        helperText="Last name of customer"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Adress"
        mapKey="adress"
        initialValue={data["adress"]}
        helperText="Adress of customer"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Phone"
        mapKey="phone"
        initialValue={data["phone"]}
        helperText="Phone number of customer"
        onEdit={onEdit}
      />
      <EditTextBox
        label="E-Mail"
        mapKey="eMail"
        initialValue={data["eMail"]}
        helperText="E-Mail adress of customer"
        onEdit={onEdit}
      />
      <EditTextBox
        label="Company"
        mapKey="company"
        initialValue={data["company"]}
        helperText="Company name of customer"
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
        <div>&nbsp; &nbsp; &nbsp;</div>
        <Button
          justify="flex-end"
          variant="outlined"
          color="primary"
          href="#outlined-buttons"
          onClick={handleDelete}
        >
          Delete
        </Button>
      </ListItem>
    </Dialog>
  );
}
