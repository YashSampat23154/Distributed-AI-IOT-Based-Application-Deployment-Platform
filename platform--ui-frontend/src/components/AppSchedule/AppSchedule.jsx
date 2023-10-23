import React, { useState, useEffect } from 'react'
import { Table, Radio, Button, Modal, Form, Input, DatePicker, TimePicker, Tag } from 'antd';
import { developerTableColumns, developerTableData, appData } from '../../data/data';
import moment, { now } from 'moment';
import axios from "axios";
const { TextArea } = Input;
const { Column, ColumnGroup } = Table;
const dateFormat = 'YYYY-MM-DD';
const timeFormat = 'HH:mm:ss';
const defaultTime = moment('09:00', 'HH:mm');
const okDeployButtonProps = {
    style: {
        backgroundColor: 'red',
        borderColor: 'red',
    },
};

const radioOptions = [
    { label: 'Daily', value: 'option1' },
    { label: 'Weekly', value: 'option2' },
    { label: 'Monthly', value: 'option3' }
];

const AppSchedule = () => {

    const [form] = Form.useForm();
    const [visible, setVisible] = useState(false);
    const [visibleModal2, setVisibleModal2] = useState(false);
    const [visibleModal3, setVisibleModal3] = useState(false);
    const [record, setRecord] = useState(null);
    const [data, setData] = useState(developerTableData);
    const [tablecols, settableCols] = useState(developerTableColumns);
    const [selectedValueRadioBtn, setSelectedValueRadioBtn] = useState('');
    const [deployInputValue, setDeployInputValue] = useState('');
    const [appSchedData, setAppScheddata] = useState(appData);

    const onChangeRadioBtn = (e, selectedValueRadioBtn = e.target.value) => {
        setSelectedValueRadioBtn(selectedValueRadioBtn);
        console.log(selectedValueRadioBtn, e.target.value);
    }

    const onDeployInputChange = (e, deployInputValue = e.target.value) => {
        setDeployInputValue(deployInputValue);
        console.log(deployInputValue, e.target.value);
    }

    const showModal = () => {
        console.log('Show Modal');
        setVisible(true);
    };

    const handleOk = () => {
        form
            .validateFields()
            .then((values) => {
                form.resetFields();
                setVisible(false);
                console.log('Received values of form: ', values);
                const newData = [...data];
                const index = newData.findIndex((item) => record.key === item.key);
                if (index > -1) {
                    const item = newData[index];
                    newData[index] = { ...item, ...values };
                    setData(newData);
                }
                setRecord(null);
            })
            .catch((info) => {
                console.log('Validate Failed:', info);
            });
    };

    const handleOkDeployed = () => {
        form
            .validateFields()
            .then((values) => {
                form.resetFields();
                setVisible(false);
                console.log('Received values of form deployed: ', values);
                const newData = [...data];
                const index = newData.findIndex((item) => record.key === item.key);
                if (index > -1) {
                    const item = newData[index];
                    item.status = 'Registered';
                    newData[index] = { ...item, ...values };
                    setData(newData);
                }
                setRecord(null);
            })
            .catch((info) => {
                console.log('Validate Failed:', info);
            });
    };

    const handleDeployNow = () => {
        setVisible(false);
        console.log('Received values of form deployed: ', record);
        const newData = [...data];
        const index = newData.findIndex((item) => record.key === item.key);
        if (index > -1) {
            const item = newData[index];
            item.status = 'Scheduled (Deploying Now)';
            newData[index] = { ...item };
            setData(newData);
        }
        appSchedData.appId = record.app_id
        appSchedData.appName = record.app_name
        appSchedData.serviceName = record.service_ids
        setRecord(null);
        axios.post("http://20.197.0.112:8013/scheduler/scheduleApp", appSchedData)
            .then((response) => {
                // Handle the server response
                console.log(response)
            })
            .catch((error) => {
                // Handle any errors
                console.log(error)
            });
    };

    const handleDeployLater = (e, visibleModal2 = true, visible = false) => {
        setVisible(visible);
        form
            .validateFields()
            .then((values) => {
                form.resetFields();
                console.log('Received values of form deployed later: ', values);
                const newData = [...data];
                const index = newData.findIndex((item) => record.key === item.key);
                if (index > -1) {
                    const item = newData[index];
                    // item.status = 'Scheduled (Deploying at given time)';
                    newData[index] = { ...item, ...values };
                    setData(newData);
                }
                // setRecord(null);
                setVisibleModal2(visibleModal2);
                console.log('Modal2:', visibleModal2);
            })
            .catch((info) => {
                console.log('Validate Failed:', info);
            });
    };

    const handleDeployPeriodic = (e, visibleModal3 = true, visible = false) => {
        setVisible(visible);
        form
            .validateFields()
            .then((values) => {
                form.resetFields();
                console.log('Received values of form deployed later: ', values);
                const newData = [...data];
                const index = newData.findIndex((item) => record.key === item.key);
                if (index > -1) {
                    const item = newData[index];
                    // item.status = 'Scheduled (Deploying at given time)';
                    newData[index] = { ...item, ...values };
                    setData(newData);
                }
                // setRecord(null);
                setVisibleModal3(visibleModal3);
                console.log('Modal3:', visibleModal3);
            })
            .catch((info) => {
                console.log('Validate Failed:', info);
            });
    };

    const handleOkDeployLater = () => {
        setVisibleModal2(false);
        setVisibleModal3(false);
        form
            .validateFields()
            .then((values) => {
                form.resetFields();
                console.log('Received values of form deployed later: ', values);
                const newData = [...data];
                const index = newData.findIndex((item) => record.key === item.key);
                if (index > -1) {
                    const item = newData[index];
                    item.status = 'Scheduled (Deploying after 5 mins)';
                    newData[index] = { ...item, ...values };
                    setData(newData);
                }
                setRecord(null);
                appSchedData.appId = record.app_id
                appSchedData.appName = record.app_name
                appSchedData.serviceName = record.service_ids
                appSchedData.startTime = now.unix() + 300
                axios.post("http://20.197.0.112:8013/scheduler/scheduleApp", appSchedData)
                    .then((response) => {
                        // Handle the server response
                        console.log(response)
                    })
                    .catch((error) => {
                        // Handle any errors
                        console.log(error)
                    });
            })
            .catch((info) => {
                console.log('Validate Failed:', info);
            });
    };


    const handleDateChange = (date, dateString) => {
        console.log(dateString);
    };

    const handleCancel = () => {
        form.resetFields();
        setVisible(false);
    };

    const handleCancelDeployLater = () => {
        form.resetFields();
        setVisibleModal2(false);
        setVisibleModal3(false);
    };

    const handleEdit = (record) => {
        console.log('Hello', record);
        setRecord(record);
        form.setFieldsValue(record);
        showModal();
    };

    const getRowClassName = (record, index) => {
        return index % 2 === 0 ? 'even-row' : 'odd-row';
    };

    const editColumn = {
        title: 'Action',
        key: 'action',
        render: (text, record) => (
            <span>
                <Button onClick={() => handleEdit(record)}>Edit</Button>
            </span>
        ),
    };

    const deployNowButton = (
        <div>
            <Button type="primary" onClick={handleDeployNow}>
                Deploy Now
            </Button>
            <Button type="primary" onClick={(e) => handleDeployLater(e, true, false)}>
                Deploy Later
            </Button>
            <Button type="primary" onClick={(e) => handleDeployPeriodic(e, true, false)}>
                Periodic Deployment
            </Button>
        </div>
    );

    const getTableData = () => {
        const url = "http://20.197.0.112:8013/fetch-app-data?app_developer_id=user_1";
        // console.log(localStorage.getItem("rollno"));
        axios.get(url).then(res => {
            console.log(res.data);
            setData(res.data);
        }).catch(error => console.log('Here-->>', error));
    }
    // useEffect(() => {
    //     //Runs only on the first render
    //     settableCols([...tablecols, editColumn]);
    //   }, []);
    useEffect(() => {
        getTableData();
    }, []);

    return (
        <div className='AppUpload'>
            <h1>Schedule Your App</h1>
            <Table
                dataSource={data} pagination={false}
                scroll={{ x: 400 }} rowClassName={getRowClassName}
                columns={[
                    ...tablecols,
                    {
                        title: 'Actions',
                        key: 'actions',
                        render: (text, record) => (
                            <Button onClick={() => handleEdit(record)}>Edit</Button>
                        ),
                    },
                ]}
            />

            {record?.status === 'registered' ?
                <div>
                    <Modal
                        title="Deploy App?"
                        open={visible}
                        onCancel={handleCancel}
                        footer={deployNowButton}
                    >
                    </Modal>
                    <Modal
                        title="Deploy Later"
                        open={visibleModal2}
                        onOk={handleOkDeployLater}
                        onCancel={handleCancelDeployLater}
                        okText="Deploy"
                    >
                        <p>Select Start Date</p>
                        <DatePicker
                            format={`${dateFormat} ${timeFormat}`}
                            showTime={{ defaultValue: moment('00:00:00', timeFormat) }}
                            onChange={handleDateChange}
                        />
                        <p>Select Stop Date</p>
                        <DatePicker
                            format={`${dateFormat} ${timeFormat}`}
                            showTime={{ defaultValue: moment('00:00:00', timeFormat) }}
                        />
                    </Modal>
                    <Modal
                        title="Periodic Deployment"
                        open={visibleModal3}
                        onOk={handleOkDeployLater}
                        onCancel={handleCancelDeployLater}
                        okText="Deploy"
                    >
                        <p>Select Start Time</p>
                        <TimePicker defaultValue={defaultTime} />
                        <p>Select Stop Time</p>
                        <TimePicker defaultValue={defaultTime} />
                        <br />
                        <br />
                        <Radio.Group options={radioOptions} value={selectedValueRadioBtn} onChange={(e) => onChangeRadioBtn(e, e.target.value)} />
                        <br />
                        <br />
                        <Input value={deployInputValue} placeholder="Leave empty if Daily selected" onChange={(e) => onDeployInputChange(e, e.target.value)} />
                    </Modal>
                </div>
                : null
            }
            {record?.status === 'deployed' ?
                <Modal
                    title="Edit Record"
                    open={visible}
                    onOk={handleOkDeployed}
                    onCancel={handleCancel}
                    okText="Undeploy"
                    okButtonProps={okDeployButtonProps}
                >
                </Modal>
                : null
            }
        </div>
    )
}

export default AppSchedule
