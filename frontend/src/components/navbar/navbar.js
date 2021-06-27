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

export default function Navbar() {
  const [selectedTab, setSelectedTab] = React.useState(0);

  const handleChange = (event, newValue) => {
    setSelectedTab(newValue);
  };
  return (
    <>
      <Toolbar width={1}>
        <IconButton>
          <img src={logo} width="42" alt="Logo" />
        </IconButton>
        <Typography variant="h6">IAS-MES</Typography>
        <Tabs value={selectedTab} onChange={handleChange}>
          <Tab label="Systemmonitoring" />
          <Tab label="Create order" />
          <Tab label="Create workingplan" />
          <Tab label="Edit workingplan" />
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
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}
