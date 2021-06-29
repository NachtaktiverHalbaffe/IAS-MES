/*
Filename: errorlogs.js
Version name: 0.1, 2021-06-29
Short description: Page to display all errors

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

export default function validateWorkingsteps(workingsteps) {
  let steps = workingsteps.sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
  let errormsg = "";
  let isValid = true;
  if (steps.length !== 0) {
    for (let i = 0; i < steps.length; i++) {
      if (i === 0 && steps[i]["task"] !== "unstore") {
        return [false, "First workingstep must be unstore"];
      } else if (steps[i]["task"] === "unstore") {
        let validator = mCheckUnstore(steps, isValid, i);
        isValid = validator[0];
        errormsg = validator[1];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "store") {
        let validator = mCheckStore(steps, isValid, i);
        isValid = validator[0];
        errormsg = validator[1];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "package") {
        let validator = mCheckPackage(steps, isValid, i);
        isValid = validator[0];
        errormsg = validator[1];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "unpackage") {
        let validator = mCheckUnpackage(steps, isValid, i);
        isValid = validator[0];
        errormsg = validator[1];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "assemble") {
        let validator = mCheckAssemble(steps, isValid, i);
        isValid = validator[0];
        errormsg = validator[1];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "color") {
        let validator = mCheckColor(steps, isValid, i);
        isValid = validator[0];
        errormsg = validator[1];
        if (!isValid) {
          return [false, errormsg];
        }
      } else if (steps[i]["task"] === "generic") {
        let validator = mCheckGeneric(steps, isValid, i);
        isValid = validator[0];
        errormsg = validator[1];
        if (!isValid) {
          return [false, errormsg];
        }
      }
    }
  }

  return [true, errormsg];
}

function mCheckUnstore(workingsteps, isValid, range) {
  let mIsValid = isValid;
  let errormsg = "";
  for (let i = 0; i < range; i++) {
    if (i !== 0) {
      if (workingsteps[i]["task"] === "store") {
        mIsValid = true;
        errormsg = "";
      }
      if (workingsteps[i]["task"] === "unstore") {
        mIsValid = false;
        errormsg = "Workingpiece must be stored before being unstored";
      }
    }
  }
  return [mIsValid, errormsg];
}

function mCheckStore(workingsteps, isValid, range) {
  let mIsValid = isValid;
  let errormsg = "";
  for (let i = 0; i < range; i++) {
    if (workingsteps[i]["task"] === "store") {
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before being stored";
    }
    if (workingsteps[i]["task"] === "unstore") {
      mIsValid = true;
      errormsg = "";
    }
  }
  return [mIsValid, errormsg];
}

function mCheckPackage(workingsteps, isValid, range) {
  let mIsValid = isValid;
  let errormsg = "";
  for (let i = 0; i < range; i++) {
    if (workingsteps[i]["task"] === "unpackage") {
      mIsValid = true;
      errormsg = "";
    }
    if (workingsteps[i]["task"] === "package") {
      mIsValid = false;
      errormsg = "Workingpiece must be unpackaged before being packaged";
    }
    if (workingsteps[i]["task"] === "unstore") {
      mIsValid = true;
      errormsg = "";
    }
    if (workingsteps[i]["task"] === "store") {
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before being packaged";
    }
  }
  return [mIsValid, errormsg];
}

function mCheckUnpackage(workingsteps, isValid, range) {
  let mIsValid = false;
  let errormsg = "Workingpiece must be packaged before being unpackaged";
  for (let i = 0; i < range; i++) {
    if (workingsteps[i]["task"] === "unpackage") {
      mIsValid = false;
      errormsg = "Workingpiece must be packaged before being unpackaged";
    }
    if (workingsteps[i]["task"] === "package") {
      mIsValid = true;
      errormsg = "";
    }
    if (workingsteps[i]["task"] === "store") {
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before being packaged";
    }
  }
  return [mIsValid, errormsg];
}

function mCheckAssemble(workingsteps, isValid, range) {
  let mIsValid = isValid;
  let errormsg = "";
  for (let i = 0; i < range; i++) {
    if (workingsteps[i]["task"] === "unpackage") {
      mIsValid = true;
      errormsg = "";
    } else if (workingsteps[i]["task"] === "package") {
      mIsValid = false;
      errormsg = "Workingpiece must be unpackaged before being assembled";
    } else if (workingsteps[i]["task"] === "store") {
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before being assembled";
    } else if (workingsteps[i]["task"] === "assemble") {
      mIsValid = false;
      errormsg = "Workingpiece must be unassembled before being assembled";
    }
  }
  return [mIsValid, errormsg];
}

function mCheckColor(workingsteps, isValid, range) {
  let mIsValid = isValid;
  let errormsg = "";
  for (let i = 0; i < range; i++) {
    if (workingsteps[i]["task"] === "unpackage") {
      mIsValid = true;
      errormsg = "";
    }
    if (workingsteps[i]["task"] === "package") {
      mIsValid = false;
      errormsg = "Workingpiece must be unpackaged before being painted";
    }
    if (workingsteps[i]["task"] === "store") {
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before being painted";
    }
  }
  return [mIsValid, errormsg];
}

function mCheckGeneric(workingsteps, isValid, range) {
  let mIsValid = isValid;
  let errormsg = "";
  for (let i = 0; i < range; i++) {
    if (workingsteps[i]["task"] === "unpackage") {
      mIsValid = true;
      errormsg = "";
    }
    if (workingsteps[i]["task"] === "package") {
      mIsValid = false;
      errormsg =
        "Workingpiece must be unpackaged before executing generic task";
    }
    if (workingsteps[i]["task"] === "store") {
      mIsValid = false;
      errormsg = "Workingpiece must be unstored before executing generic task";
    }
  }
  return [mIsValid, errormsg];
}
