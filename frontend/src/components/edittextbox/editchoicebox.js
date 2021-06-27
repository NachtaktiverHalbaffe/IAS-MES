/*
Filename: editchoicebox.js
Version name: 0.1, 2021-06-27
Short description: Component for text input with choices to select

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { ListItem, TextField } from "@material-ui/core";

export default function EditChoiceBox(props) {
  const { onEdit, label, initialValue, helperText, mapKey, choices } = props;
  const [value, setValue] = React.useState(initialValue);

  const handleChange = (event) => {
    setValue(event.target.value);
    onEdit(mapKey, event.target.value);
  };

  return (
    <ListItem>
      <TextField
        id="outlined-full-width"
        label={label}
        select
        style={{ margin: 8 }}
        defaultValue={initialValue}
        helperText={helperText}
        fullWidth
        margin="normal"
        InputLabelProps={{
          shrink: true,
        }}
        variant="outlined"
        value={value}
        onChange={handleChange}
      >
        {choices.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </TextField>
    </ListItem>
  );
}
