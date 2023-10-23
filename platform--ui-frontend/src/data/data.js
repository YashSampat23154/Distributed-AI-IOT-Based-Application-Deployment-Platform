import {
  UilEstate,
  UilClipboardAlt,
  UilUserAlt,
  UilPackage,
  UilChart,
  UilSignOutAll,
  UilUsdSquare,
  UilMoneyWithdrawal,
  UilRegistered,
  UilServer,
  UilWifiRouter,
  UilSchedule,
  UilUpload,
  UilDocumentInfo
} from "@iconscout/react-unicons";
import moment from "moment";


const now = moment();
//Sidebar data
export const Sidebardata = [
  {
    icon: UilEstate,
    heading: "Dashboard",
    link: "dashboard",
  },
  // {
  //   icon: UilPackage,
  //   heading: "Sensor Registration",
  //   link: "sensor-reg",
  // },
  {
    icon: UilUpload,
    heading: "Upload Application",
    link: "uploadapp",
  },
  {
    icon: UilSchedule,
    heading: "Schedule Application",
    link: "appschedule",
  },
  {
    icon: UilDocumentInfo,
    heading: "Developer Docs",
    link: "developer-docs",
  },
  {
    icon: UilChart,
    heading: "Analytics",
    link: "analytics",
  },
  {
    icon: UilChart,
    heading: "Logs",
    link: "logs",
  },
];

//Developer Sidebar data
export const developerSidebardata = [
  {
    icon: UilEstate,
    heading: "Dashboard",
    link: "dashboard",
  },
  {
    icon: UilUpload,
    heading: "Upload Application",
    link: "uploadapp",
  },
  {
    icon: UilSchedule,
    heading: "Schedule Application",
    link: "appschedule",
  },
  {
    icon: UilDocumentInfo,
    heading: "Developer Docs",
    link: "developer-docs",
  },
  {
    icon: UilChart,
    heading: "Analytics",
    link: "analytics",
  }
];

//Developer Sidebar data
export const adminSidebardata = [
  {
    icon: UilPackage,
    heading: "Sensor Registration",
    link: "sensor-reg",
  },
  {
    icon: UilChart,
    heading: "Logs",
    link: "logs",
  },
];

export const CardsData = [
  {
    title: "Applications Registered",
    color: {
      backGround: "linear-gradient(180deg, #bb67ff 0%, #c484f3 100%)",
      boxShadow: "0px 10px 20px 0px #e0c6f5",
    },
    barValue: 70,
    value: "1",
    png: UilRegistered,
    series: [
      {
        name: "Sales",
        data: [31, 40, 28, 51, 42, 109, 100],
      },
    ],
  },
  {
    title: "Applications Deployed",
    color: {
      backGround: "linear-gradient(180deg, #FF919D 0%, #FC929D 100%)",
      boxShadow: "0px 10px 20px 0px #FDC0C7",
    },
    barValue: 80,
    value: "1",
    png: UilServer,
    series: [
      {
        name: "Revenue",
        data: [10, 100, 50, 70, 80, 30, 40],
      },
    ],
  },
  {
    title: "Sensors Registered",
    color: {
      backGround:
        "linear-gradient(rgb(248, 212, 154) -146.42%, rgb(255 202 113) -46.42%)",
      boxShadow: "0px 10px 20px 0px #F9D59B",
    },
    barValue: 60,
    value: "14",
    png: UilWifiRouter,
    series: [
      {
        name: "Expenses",
        data: [10, 25, 15, 30, 12, 15, 20],
      },
    ],
  },
];

export const developerTableColumns = [
  {
    title: "AppID",
    dataIndex: "app_id",
    key: "app_id",
  },
  {
    title: "AppName",
    dataIndex: "app_name",
    key: "app_name",
  },
  {
    title: "Sensors Registered",
    dataIndex: "sensors_registered",
    key: "sensors_registered",
  },
  {
    title: "App Services",
    dataIndex: "service_ids",
    key: "service_ids",
  },
  {
    title: "Status",
    dataIndex: "status",
    key: "status",
  },
];

export const developerTableData = [
  {
  }
];


export const Subsystem_Names = [
  {
    name: "API Gateway",
    link: "api-gateway",
  },
  {
    name: "Deployer",
    link: "deployer",
  },
  {
    name: "Load Balancer",
    link: "load-balancer",
  },
  {
    name: "Node Manager",
    link: "node-manager",
  },
  {
    name: "Scheduler",
    link: "scheduler",
  },
  {
    name: "Sensor Manager",
    link: "sensor-manager",
  },
  {
    name: "Validator Workflow",
    link: "validator-workflow",
  },
  {
    name: "Bootstrapper",
    link: "bootstrapper",
  },
  {
    name: "Monitoring & Fault Tolerance",
    link: "monitoring-fault-tolerance",
  },
];


export const appData = {
  "appId": "7ae7f8e4-dd37-11ed-8523-e4e749421b6a",
  "serviceName": ['foo', 'random_rating', 'bar', 'w1'],
  "appName": "app13",
  "startTime": now.unix(),
  "endTime": null,
  "isPeriodic": 0,
  "periodicity": 1,
  "now": 1,
  "scheduleType": 1
};

//Deploy Later
// {
//   "appId": "7ae7f8e4-dd37-11ed-8523-e4e749421b6a",
//   "serviceName": ['foo', 'random_rating', 'bar', 'w1'],
//   "appName": "app13",
//   "startTime": now.unix(),
//   "endTime": null,
//   "isPeriodic": 0,
//   "periodicity": 1,
//   "now": 0,
//   "scheduleType": 1
// }


//Deploy Periodic
// {
//   "appId": "7ae7f8e4-dd37-11ed-8523-e4e749421b6a",
//   "serviceName": ['foo', 'random_rating', 'bar', 'w1'],
//   "appName": "app13",
//   "startTime": now.unix(),
//   "endTime": null,
//   "isPeriodic": 1,
//   "periodicity": 1,
//   "now": 1,
//   "scheduleType": 1
// }

const configFileData = {
  "language": "python:3.9",
  "workdir": "/myapp",
  "port": "8001",
  "command": "python3 /myapp/s1.py",
  "packages_file_path": "/myapp/req.txt",
  "package_installation_cmd": "pip install -r /myapp/req.txt"
};

const appConfigFileData = {
  "applicationName": "app13",
  "services": [
    {
      "name": "app",
      "files": ["app.py", "requirements.txt", "config.json"],
      "endpoint": "/server",
      "parameters": [
        {
          "name": "appId",
          "dataType": "str"
        },
        {
          "name": "serviceName",
          "dataType": "str"
        },
        {
          "name": "requestData",
          "dataType": "dict"
        }
      ],
      "sensors": [],
      "outputs": [
        {
          "name": "res",
          "dataType": "dict"
        }
      ]
    },
    {
      "name": "foo",
      "files": ["foo.py", "requirements.txt", "config.json"],
      "endpoint": "/foo",
      "parameters": [
        {
          "name": "par_1",
          "dataType": "int"
        }
      ],
      "sensors": [
        {
          "sensor_type": "WM",
          "lat": 45,
          "long": 50
        }
      ],
      "outputs": [
        {
          "name": "res1",
          "dataType": "str"
        },
        {
          "name": "res2",
          "dataType": "int"
        }
      ]
    },
    {
      "name": "random_rating",
      "files": ["random_rating.py", "requirements.txt", "config.json"],
      "endpoint": "/random_rating",
      "parameters": [],
      "sensors": [],
      "outputs": [
        {
          "name": "res1",
          "dataType": "int"
        }
      ]
    },
    {
      "name": "bar",
      "files": ["bar.py", "requirements.txt", "config.json"],
      "endpoint": "/bar",
      "parameters": [
        {
          "name": "par_1",
          "dataType": "str"
        },
        {
          "name": "par_2",
          "dataType": "int"
        }
      ],
      "sensors": [
        {
          "sensor_type": "AQ",
          "lat": 45,
          "long": 50
        },
        {
          "sensor_type": "AQ",
          "lat": 36,
          "long": 80
        }
      ],
      "outputs": [
        {
          "name": "res1",
          "dataType": "int"
        }
      ]
    }
  ],
  "workflows": ["w1.json"],
  "developer_id": "user_1"
};

const workflowData = {
  "workflowName" : "w1",
  "workflowInputs" : [
      {
          "name": "appId",
          "dataType": "str",
          "required" : true
      },
      {
          "name": "x",
          "dataType": "int"
      },
      {
          "name": "y",
          "dataType": "str"
      }
  ],
  "services": [
      {
          "serviceName": "foo",
          "endpoint" : "/foo",
          "parameters": [
              {
                  "name":"par_1",
                  "dataType":"int",
                  "prevOutput" : false,
                  "prevServiceName" : null,
                  "prevOutputName": null,
                  "workflowInputName" :  "x"
              }            
          ],
          "outputs": [
              {
                  "name":"res1",
                  "dataType":"str"
              },
              {
                  "name" : "res2",
                  "dataType" : "int"
              }            
          ]
      },
      {
          "serviceName": "bar",
          "endpoint" : "/bar",
          "parameters": [
              {
                  "name":"par_1",
                  "dataType":"str",
                  "prevOutput" : true,
                  "prevServiceName" : "foo",
                  "prevOutputName": "res1",
                  "workflowInputName" :  null
              },
              {
                  "name":"par_2",
                  "dataType":"int",
                  "prevOutput" : false,
                  "prevServiceName" : null,
                  "prevOutputName": null,
                  "workflowInputName" :  "y"
              }               
          ],
          "outputs": [
              {
                  "name": "res1",
                  "dataType": "int"
              }
          ]
      },
      {
          "serviceName": "random_rating",
          "endpoint" : "/random_rating",
          "parameters": [],
          "outputs": [
              {
                  "name": "res1",
                  "dataType": "int"
              }
          ]
      }
  ],
  "workflowOuputs": [
      {
          "serviceName": "foo",
          "serviceParName" : "res2",
          "parameterName" : "inferene1"
      },
      {
          "serviceName": "bar",
          "serviceParName": "res1",
          "parameterName" : "inferene2"
      },
      {
          "serviceName": "random_rating",
          "serviceParName": "res1",
          "parameterName" : "inferene3"
      }
  ]
};


export const developerDocsData = [
  {
    heading: 'sample requirements.txt(should be there in service folder)',
    text: 'anyio==3.6.2\nclick==8.1.3\nfastapi==0.94.0\nh11==0.14.0\nidna==3.4\npydantic==1.10.6\nsniffio==1.3.0\nstarlette==0.26.0.post1\ntyping_extensions==4.5.0\nuvicorn==0.21.0'
  },
  {
    heading: 'sample config.json(that should come under each service)',
    text: JSON.stringify(configFileData, null, 2)
  },
  {
    heading: 'sample appConfig.json',
    text: JSON.stringify(appConfigFileData, null, 2)
  },
  {
    heading: 'Sample worfklow.json',
    text: JSON.stringify(workflowData, null, 2)
  },
];
export const deployer_instance = 
{
  subsystem_name: 'Deployer',
  instance_list: 
  [
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
    {instance_id: "deployer_2023-1-22_12:12:12.34"},
  ]
}