import React, { useState } from 'react';
import { Typography, Collapse } from 'antd';
import { developerDocsData } from '../../data/data';
const { Text } = Typography;
const { Panel } = Collapse;

//Light-pink:#FFE5E5
//Wheat: #f5deb3
const customPanelStyle = {
    background: '#FFE5E5',
    border: 0,
    fontWeight: 'bold',
    fontSize: '17px'
  };
const DeveloperDocs = () => {
    const [devData, setDevData] = useState(developerDocsData);
    return (
        <div className='AppUpload'>
            <h1>Developer Documentation</h1>
            <Collapse accordion>
                {devData.map((data, index) => (
                    <Panel header={data.heading} key={index} style={customPanelStyle}>
                        <Text>
                            <div style={{ overflow: 'auto', height: '400px', width: '900px' }}>
                                <pre>{data.text}</pre>
                            </div>
                        </Text>
                    </Panel>
                ))}
            </Collapse>

        </div>
    )
}

export default DeveloperDocs;
