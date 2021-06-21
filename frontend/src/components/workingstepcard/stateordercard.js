/*
Filename: stateordercard.js
Version name: 0.1, 2021-06-21
Short description: Card component for a specific working step

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import Box from "@material-ui/core/Box";
import { Grid, Paper } from "@material-ui/core";
import CardActionArea from "@material-ui/core/CardActionArea";
import CardContent from "@material-ui/core/CardContent";
import DialogTitle from "@material-ui/core/DialogTitle";
import Dialog from "@material-ui/core/Dialog";
import Typography from "@material-ui/core/Typography";
import { TextField } from "@material-ui/core";

export default function StateOrderCard(props) {
  let name = "";
  let description = "";
  let orderNo = 0;
  let orderPos = 0;
  let costumer = "";
  let assignedAt = "";

  const [open, setOpen] = React.useState(false);
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
        <EditStateOrderDialog open={open} onClose={handleClose} data={data} />
      </Paper>
    </Box>
  );
}

function EditStateOrderDialog(props) {
  const { onClose, value, open, data } = props;

  const handleClose = () => {
    onClose(data);
  };

  return (
    <Dialog
      onClose={handleClose}
      aria-labelledby="simple-dialog-title"
      open={open}
    >
      <DialogTitle id="simple-dialog-title">Edit order</DialogTitle>
    </Dialog>
  );
}
