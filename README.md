[![StackStorm](https://github.com/stackstorm/st2/raw/master/stackstorm_logo.png)](http://www.stackstorm.com)

# Read me 

This pack allows you to create multi-chassis trunking between two netiron devices. through stackstorm 

## Configuration

edit the excel sheet named details with the right configuration and save it. 
the pack contains a python script that will read the excel sheet and translate the information to the right commands.


------
The pack has a workflow that is triggered manually and will start configuring session vlan, ICLs, Keep alive vlan, LAGs, tagging ports with the right vlans and creating the MCT cluster

## This is a BETA Version yet and undergoing some modifications ##

## Actions

- Create_session
- Create_keep_alive
- Create_lags
- Create_cluster

