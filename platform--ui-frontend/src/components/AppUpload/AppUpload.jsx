import React, { useState, useEffect } from 'react';
import './AppUpload.css';
import axios from "axios";
import { UploadOutlined, InboxOutlined, DownloadOutlined } from '@ant-design/icons';
import { Button, Upload, message, Space, Table, Tag, Pagination, Typography, Collapse } from 'antd';
import { developerTableColumns, developerTableData } from '../../data/data'
const { Column, ColumnGroup } = Table;
const { Text } = Typography;
const { Panel } = Collapse;
const PAGE_SIZE = 7;

const AppUpload = () => {

    const [file, setFile] = useState(null);
    const [tableData, setTableData] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [apiData, setApiData] = useState(null);
    const [messageApi, ContextHolder] = message.useMessage();

    const info = (msg) => {
        messageApi.info(msg);
    };

    const handleDataChange = (newData) => {
        setTableData(newData);
    };

    const handleChangePage = (page) => {
        setCurrentPage(page);
    };
    const handleFileChange = (event) => {
        const selectedFile = event.target.files[0];
        setFile(selectedFile);
    };

    const getTableData = () => {
        const url = "http://20.197.0.112:8013/fetch-app-data?app_developer_id=user_1";
        // console.log(localStorage.getItem("rollno"));
        axios.get(url).then(res => {
            console.log(res.data);
            setTableData(res.data);
        }).catch(error => console.log('Here-->>', error));
    }

    useEffect(() => {
        getTableData();
    }, []);

    const fileData = () => {

        if (file) {
            return (
                <div>
                    <h2>File Details:</h2>
                    <p>File Name: {file.name}</p>

                    <p>File Type: {file.type}</p>

                    <p>
                        Last Modified:{" "}
                        {file.lastModifiedDate.toDateString()}
                    </p>

                </div>
            );
        } else {
            return (
                <div>
                    <h4>Choose before Pressing the Upload button</h4>
                </div>
            );
        }
    };

    const getRowClassName = (record, index) => {
        return index % 2 === 0 ? 'even-row' : 'odd-row';
    };

    const getPaginatedData = () => {
        const startIndex = (currentPage - 1) * PAGE_SIZE;
        const endIndex = startIndex + PAGE_SIZE;
        console.log(startIndex, endIndex);
        return tableData.slice(startIndex, endIndex);
    };

    const handleUpload = () => {
        const formData = new FormData();
        formData.append("file", file);
        console.log(fileData);
        // formData.append("appName", "app13");
        // Add any additional form data here
        console.log(formData.entries().next().value);
        if (formData.entries().next().value[1] == "null") {
            console.log('No file');
            info('Upload App zip file first!');
        }
        else {
            axios.post("http://20.197.0.112:8013/validator-workflow/upload", formData, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            })
                .then((response) => {
                    // Handle the server response
                    console.log(response);
                    info('Zip File Uploaded Successfully!!');
                })
                .catch((error) => {
                    // Handle any errors
                    console.log(error)
                });
        }
    };

    const paginationSettings = {
        pageSize: 5, // number of rows per page
        showSizeChanger: true, // allow user to change page size
        pageSizeOptions: ['3', '5', '10'], // available page sizes
        showQuickJumper: true, // allow user to jump to a specific page
        // ... other pagination settings
    };

    return (
        <div className='AppUpload'>
            {ContextHolder}
            <h1>Upload Your App</h1>
            <div className='fileUpload'>
                <input type="file" onChange={handleFileChange} />
                <Button onClick={handleUpload} type="primary" icon={<DownloadOutlined />} size='middle'>
                    Upload
                </Button>
                {fileData()}
                <br />
                <h4>Uploaded Application Status</h4>
                <Table
                    dataSource={tableData} pagination={paginationSettings}
                    rowClassName={getRowClassName}
                >
                    <Column title="AppID" dataIndex="app_id" key="app_id" />
                    <Column title="AppName" dataIndex="app_name" key="app_name" />
                    <Column title="Sensors Registered" dataIndex="sensors_registered" key="sensors_registered"
                        // render={(sensors_registered) => (
                        //     <>
                        //         {sensors_registered.map((sensor) => (
                        //             <Tag color="blue" key={sensors_registered}>
                        //                 {sensor}
                        //             </Tag>
                        //         ))}
                        //     </>
                        // )}
                    />
                    <Column title="App Services" dataIndex="service_ids" key="service_ids"
                        render={(service_ids) => (
                            <>
                                {service_ids.map((service) => (
                                    <Tag color="blue" key={service_ids}>
                                        {service}
                                    </Tag>
                                ))}
                            </>
                        )}
                    />
                    <Column title="Status" dataIndex="status" key="status" />
                </Table>
            </div>
        </div>
    )
}

export default AppUpload
