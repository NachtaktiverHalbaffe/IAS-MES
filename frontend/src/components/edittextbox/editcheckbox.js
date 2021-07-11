/*
Filename: editcheckbox.js
Version name: 1.0, 2021-07-10
Short description: Component to check or uncheck an option

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import { ListItem, FormControlLabel, Checkbox } from "@material-ui/core";

export default function EditCheckBox(props) {
  const { onEdit, label, initialValue, mapKey } = props;
  const [value, setValue] = React.useState(initialValue);

  // callback when checkbox gets checked/unchecked
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
