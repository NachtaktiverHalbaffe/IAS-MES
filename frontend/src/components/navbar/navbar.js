/*
Filename: navbar.js
Version name: 1.0, 2021-07-10
Short description: navbar for navigation and tabs with the pages

(C) 2003-2021 IAS, Universitaet Stuttgart

*/

import React from "react";
import Toolbar from "@material-ui/core/Toolbar";
import logo from "../../assets/logo.png";
import Typography from "@material-ui/core/Typography";
import { IconButton } from "@material-ui/core";
import Tabs from "@material-ui/core/Tabs";
import Tab from "@material-ui/core/Tab";
import Box from "@material-ui/core/Box";

import SystemMonitoring from "../../pages/systemmonitoring/systemmonitoring";
import CreateOrder from "../../pages/createorder/createorder";
import CreateWorkingPlan from "../../pages/createworkingplan/createworkingplan";
import EditWorkingPlan from "../../pages/editworkingplan/editworkingplan";
import ErrorLogs from "../../pages/errorlogs/errorlogs";
import Settings from "../../pages/settings/settings";

export default function Navbar() {
  const [selectedTab, setSelectedTab] = React.useState(0);

  // callback function when a new tab is selected
  const handleChange = (event, newValue) => {
    setSelectedTab(newValue);
  };
  return (
    <>
      <Toolbar width={1}>
        <IconButton>
          <img src={logo} width="42" alt="Logo" />
        </IconButton>
        <Typography variant="h6" component={"span"}>
          IAS-MES
        </Typography>
        <Tabs value={selectedTab} onChange={handleChange}>
          <Tab label="Systemmonitoring" />
          <Tab label="Create order" />
          <Tab label="Create workingplan" />
          <Tab label="Edit workingplan" />
          <Tab label="Error logs" />
          <Tab label="Settings" />
        </Tabs>
      </Toolbar>
      <TabPanel value={selectedTab} index={0}>
        <SystemMonitoring />
      </TabPanel>
      <TabPanel value={selectedTab} index={1}>
        <CreateOrder />
      </TabPanel>
      <TabPanel value={selectedTab} index={2}>
        <CreateWorkingPlan />
      </TabPanel>
      <TabPanel value={selectedTab} index={3}>
        <EditWorkingPlan />
      </TabPanel>
      <TabPanel value={selectedTab} index={4}>
        <ErrorLogs />
      </TabPanel>
      <TabPanel value={selectedTab} index={5}>
        <Settings />
      </TabPanel>
    </>
  );
}

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box p={3}>
          <Typography component={"span"}>{children}</Typography>
        </Box>
      )}
    </div>
  );
}
