/*
Filename: validateWorkingSteps.js
Version name: 0.1, 2021-07-05
Short description: Function to validate workingplan that it is executable

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

export default function (workingSteps, workingPiece) {
  let steps = workingSteps[0].sort((a, b) => (a.stepNo > b.stepNo ? 1 : -1));
  let requiredState = {
    isAssembled: null,
    isPackaged: null,
  };

  // get the required state the workingpiece needs to have
  for (let i = 0; i < steps.length; i++) {
    if (steps[i].task === "assemble") {
      if (requiredState["isAssembled"] == null) {
        requiredState["isAssembled"] = false;
      }
    } else if (steps[i].task === "generic") {
      if (requiredState["isAssembled"] == null) {
        requiredState["isAssembled"] = true;
      }
    } else if (steps[i].task === "package") {
      if (requiredState["isPackaged"] == null) {
        requiredState["isPackaged"] = false;
      }
    } else if (steps[i].task === "unpackage") {
      if (requiredState["isPackaged"] == null) {
        requiredState["isPackaged"] = true;
      }
    }
  }
  console.log(requiredState);
  // check if workingpiece has the right state
  if (requiredState.isAssembled != null) {
    if (workingPiece.isAssembled !== requiredState.isAssembled) {
      if (requiredState.isAssembled === false) {
        return [false, "Workingpiece needs to be disassembled"];
      } else {
        return [false, "Workingpiece needs to be assembled"];
      }
    }
  }
  if (requiredState.isPackaged != null) {
    if (
      workingPiece.isPackaged !== requiredState.isPackaged &&
      requiredState.isPackaged !== null
    ) {
      if (requiredState.isPackaged === false) {
        return [false, "Workingpiece needs to be unpackaged"];
      } else {
        return [false, "Workingpiece needs to be packaged"];
      }
    }
  }

  return [true, ""];
}
