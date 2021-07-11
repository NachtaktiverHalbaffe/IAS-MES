/*
Filename: edittextbox.js
Version name: 1.0, 2021-07-10
Short description: Component for text input

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { ListItem, TextField } from "@material-ui/core";

export default function EditTextBox(props) {
  const { onEdit, label, initialValue, helperText, mapKey } = props;
  const [value, setValue] = React.useState(initialValue);

  // callback when value of textfiled gets changed
  const handleChange = (event) => {
    setValue(event.target.value);
    onEdit(mapKey, event.target.value);
  };

  return (
    <ListItem>
      <TextField
        id="outlined-full-width"
        label={label}
        style={{ margin: 8 }}
        helperText={helperText}
        fullWidth
        margin="normal"
        InputLabelProps={{
          shrink: true,
        }}
        variant="outlined"
        value={value}
        onChange={handleChange}
      />
    </ListItem>
  );
}
