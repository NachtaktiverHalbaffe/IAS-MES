import React from "react";
import { Snackbar } from "@material-ui/core";
import MuiAlert from "@material-ui/lab/Alert";

import { AUTO_HIDE_DURATION } from "../../const";

function Alert(props) {
  return <MuiAlert elevation={6} variant="filled" {...props} />;
}

export default function ErrorSnackbar(props) {
  // level can be "warning", "error","info" or "sucess"
  const { isOpen, level, message } = props;
  const [open, setOpen] = React.useState(isOpen);

  // React.useEffect(() => {
  //   if (isOpen && !open) {
  //     setOpen(true);
  //   }
  // }, []);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setOpen(false);
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={AUTO_HIDE_DURATION}
      onClose={handleClose}
    >
      <Alert severity={level} onClose={handleClose}>
        {message}
      </Alert>
    </Snackbar>
  );
}
