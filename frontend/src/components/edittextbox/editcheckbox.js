/*
Filename: editchoicebox.js
Version name: 0.1, 2021-06-27
Short description: Component for text input with choices to select

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { ListItem, FormControlLabel, Checkbox } from "@material-ui/core";

export default function EditCheckBox(props) {
  const { onEdit, label, initialValue, mapKey } = props;
  const [value, setValue] = React.useState(initialValue);

  const handleChange = (event) => {
    setValue(event.target.checked);
    onEdit(mapKey, event.target.checked);
  };

  return (
    <ListItem>
      <FormControlLabel
        control={
          <Checkbox
            checked={value}
            onChange={handleChange}
            name="checkedB"
            color="primary"
          />
        }
        label={label}
      />
    </ListItem>
  );
}
