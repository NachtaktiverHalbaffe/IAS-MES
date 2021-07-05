/*
Filename: errorlogs.js
Version name: 0.1, 2021-06-29
Short description: Page to display all errors

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

export default function validateWorkingsteps(workingsteps) {
  let steps = workingsteps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
  let state = {
    isAssembled: null,
    isPackaged: null,
    isStored: null,
  };
  let errormsg = "";
  let isValid = true;
  if (steps.length !== 0) {
    for (let i = 0; i < steps.length; i++) {
      if (i === 0 && steps[i]["task"] !== "unstore") {
        return [false, "First workingstep must be unstore"];
      } else if (steps[i]["task"] === "unstore") {
        let validator = mCheckUnstore(steps, i + 1, state);
        isValid = validator[0];
        errormsg = validator[1];
        state = validator[2];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "store") {
        let validator = mCheckStore(steps, i + 1, state);
        isValid = validator[0];
        errormsg = validator[1];
        state = validator[2];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "package") {
        let validator = mCheckPackage(steps, i + 1, state);
        isValid = validator[0];
        errormsg = validator[1];
        state = validator[2];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "unpackage") {
        let validator = mCheckUnpackage(steps, i + 1, state);
        isValid = validator[0];
        errormsg = validator[1];
        state = validator[2];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "assemble") {
        let validator = mCheckAssemble(steps, i + 1, state);
        isValid = validator[0];
        errormsg = validator[1];
        state = validator[2];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "color") {
        let validator = mCheckColor(steps, i + 1, state);
        isValid = validator[0];
        errormsg = validator[1];
        state = validator[2];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "generic") {
        let validator = mCheckGeneric(steps, i + 1, state);
        isValid = validator[0];
        errormsg = validator[1];
        state = validator[2];
        if (!isValid) {
          return [false, errormsg];
        }
      }
    }
  }

  return [true, errormsg];
}

function mCheckUnstore(workingsteps, range, state) {
  let mIsValid = true;
  let errormsg = "";
  let newState = state;
  for (let i = 0; i < range; i++) {
    if (i !== 0) {
      // validating
      if (workingsteps[i]["task"] === "store") {
        newState["isStored"] = true;
        mIsValid = true;
        errormsg = "";
      } else if (workingsteps[i]["task"] === "unstore") {
        if (newState["isStored"] === true) {
          mIsValid = true;
          newState["isStored"] = false;
          errormsg = "";
        } else {
          mIsValid = false;
          errormsg = "Workingpiece must be stored before being unstored";
        }
      }
      // state tracking
      else if (workingsteps[i]["task"] === "assemble") {
        newState["isAssembled"] = true;
      } else if (workingsteps[i]["task"] === "generic") {
        newState["isAssembled"] = false;
      } else if (workingsteps[i]["task"] === "package") {
        newState["isPackaged"] = true;
      } else if (workingsteps[i]["task"] === "unpackage") {
        newState["isPackaged"] = false;
      }
    }
  }
  return [mIsValid, errormsg, newState];
}

function mCheckStore(workingsteps, range, state) {
  let mIsValid = true;
  let errormsg = "";
  let newState = state;
  for (let i = 0; i < range; i++) {
    // validating
    if (workingsteps[i]["task"] === "store") {
      if (newState["isStored"] == true) {
        mIsValid = false;
        errormsg = "Workingpiece must be unstored before being stored";
      }
      newState["isStored"] = true;
    } else if (workingsteps[i]["task"] === "unstore") {
      if (newState["isStored"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isStored"] = false;
      // state tracking
    } else if (workingsteps[i]["task"] === "assemble") {
      newState["isAssembled"] = true;
    } else if (workingsteps[i]["task"] === "generic") {
      newState["isAssembled"] = false;
    } else if (workingsteps[i]["task"] === "package") {
      newState["isPackaged"] = true;
    } else if (workingsteps[i]["task"] === "unpackage") {
      newState["isPackaged"] = false;
    }
  }
  return [mIsValid, errormsg, newState];
}

function mCheckPackage(workingsteps, range, state) {
  let mIsValid = true;
  let errormsg = "";
  let newState = state;
  for (let i = 0; i < range; i++) {
    // validating
    if (workingsteps[i]["task"] === "unpackage") {
      if (newState["isPackaged"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isPackaged"] = false;
    } else if (workingsteps[i]["task"] === "package") {
      if (newState["isPackaged"] == true) {
        mIsValid = false;
        errormsg = "Workingpiece must be unpackaged before being packaged";
      }
      newState["isPackaged"] = true;
    } else if (workingsteps[i]["task"] === "unstore") {
      if (newState["isStored"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isStored"] = false;
    } else if (workingsteps[i]["task"] === "store") {
      newState["isStored"] = true;
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before executing generic task";
    }
    // state tracking
    else if (workingsteps[i]["task"] === "assemble") {
      newState["isAssembled"] = true;
    } else if (workingsteps[i]["task"] === "generic") {
      newState["isAssembled"] = false;
    }
  }
  return [mIsValid, errormsg, newState];
}

function mCheckUnpackage(workingsteps, range, state) {
  let mIsValid = true;
  let errormsg = "";
  let newState = state;
  for (let i = 0; i < range; i++) {
    // validating
    if (workingsteps[i]["task"] === "unpackage") {
      if (newState["isPackaged"] == false) {
        mIsValid = false;
        errormsg = "Workingpiece must be packaged before being unpackaged";
      }
      newState["isPackaged"] = false;
    } else if (workingsteps[i]["task"] === "package") {
      if (newState["isPackaged"] == false) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isPackaged"] = true;
    } else if (workingsteps[i]["task"] === "store") {
      newState["isStored"] = true;
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before executing generic task";
    } else if (workingsteps[i]["task"] === "unstore") {
      if (newState["isStored"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isStored"] = false;
    }
    // state tracking
    else if (workingsteps[i]["task"] === "assemble") {
      newState["isAssembled"] = true;
    } else if (workingsteps[i]["task"] === "generic") {
      newState["isAssembled"] = false;
    }
  }
  return [mIsValid, errormsg, newState];
}

function mCheckAssemble(workingsteps, range, state) {
  let mIsValid = true;
  let errormsg = "";
  let newState = state;
  for (let i = 0; i < range; i++) {
    // validating
    if (workingsteps[i]["task"] === "unpackage") {
      if (newState["isPackaged"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isPackaged"] = false;
    } else if (workingsteps[i]["task"] === "package") {
      mIsValid = false;
      errormsg = "Workingpiece must be unpackaged before executing assemble";
      newState["isPackaged"] = true;
    } else if (workingsteps[i]["task"] === "store") {
      newState["isStored"] = true;
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before executing assemble";
    } else if (workingsteps[i]["task"] === "unstore") {
      if (newState["isStored"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isStored"] = false;
    } else if (workingsteps[i]["task"] === "assemble") {
      if (newState["isAssembled"] == true) {
        mIsValid = false;
        errormsg = "Workingpiece must be disassembled before being assembled";
      }
      newState["isAssembled"] = true;
    } else if (workingsteps[i]["task"] === "generic") {
      if (newState["isAssembled"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isAssembled"] = false;
    }
  }
  return [mIsValid, errormsg, newState];
}

function mCheckColor(workingsteps, range, state) {
  let mIsValid = true;
  let errormsg = "";
  let newState = state;
  for (let i = 0; i < range; i++) {
    // validating
    if (workingsteps[i]["task"] === "unpackage") {
      if (newState["isPackaged"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isPackaged"] = false;
    } else if (workingsteps[i]["task"] === "package") {
      mIsValid = false;
      newState["isPackaged"] = true;
      errormsg = "Workingpiece must be unpackaged before being painted";
    } else if (workingsteps[i]["task"] === "store") {
      newState["isStored"] = true;
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before executing generic task";
    } else if (workingsteps[i]["task"] === "unstore") {
      if (newState["isStored"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isStored"] = false;
    }
    // state tracking
    else if (workingsteps[i]["task"] === "assemble") {
      newState["isAssembled"] = true;
    } else if (workingsteps[i]["task"] === "genric") {
      newState["isAssembled"] = false;
    }
  }
  return [mIsValid, errormsg, newState];
}

function mCheckGeneric(workingsteps, range, state) {
  let mIsValid = true;
  let errormsg = "";
  let newState = state;
  for (let i = 0; i < range; i++) {
    // validating
    if (workingsteps[i]["task"] === "unpackage") {
      if (newState["isPackaged"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isPackaged"] = false;
    } else if (workingsteps[i]["task"] === "package") {
      newState["isPackaged"] = true;
      mIsValid = false;
      errormsg =
        "Workingpiece must be unpackaged before executing generic task";
    } else if (workingsteps[i]["task"] === "store") {
      newState["isStored"] = true;
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before executing generic task";
    } else if (workingsteps[i]["task"] === "unstore") {
      if (newState["isStored"] == true) {
        mIsValid = true;
        errormsg = "";
      }
      newState["isStored"] = false;
    }
    // state tracking
    else if (workingsteps[i]["task"] === "assemble") {
      newState["isAssembled"] = true;
    } else if (workingsteps[i]["task"] === "generic") {
      newState["isAssembled"] = true;
    }
  }
  return [mIsValid, errormsg, newState];
}
