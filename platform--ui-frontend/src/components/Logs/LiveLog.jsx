import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {Button} from 'antd'
import axios from "axios";

const LiveLog = () => {
  const { subsystem, instance } = useParams();
  const [showLogs, setShowLogs] = useState(false)
  const [incomingLogs, setIncomingLogs] = useState('')
  const [loading, setLoading] = useState(true)
  const [counter, setCounter] = useState(0)

  const extract_time=()=>{
    const myArray = instance.split("_");
    return myArray[1]
  }

  const time = extract_time()
  const getLogs = () => {
    return axios
      .get("http://127.0.0.1:5000/live-logs?subsystem_name="+subsystem+"&start_time=" + time)
      .then((response) => {
        setIncomingLogs(response.data.logs);
        setLoading(false)
        console.log(response.data.logs);
        // setLoading(false);
      })
      .catch((error) => console.log(error));
  }
  const delay = ms => new Promise(
    resolve => setTimeout(resolve, ms)
  );
  const updateCounter= async()=>{
    while(true){
      setCounter(c => c+1)
      await delay(2000)
    }
  }
  useEffect(()=>{
    updateCounter()
  },[])

  useEffect(()=>{
    if (showLogs)
      getLogs()
    // console.log(counter)

  },[showLogs, counter])

  return (
    <div>
      <header>
        <h2>
          {subsystem} / {instance}
        </h2>
        <div>

        <Button type="primary" onClick={()=>setShowLogs((pre)=> !pre)}>{showLogs ? 'Stop' : 'Show Live Log'}</Button>
        </div>
      </header>
      <div className='display_box'>
      {loading ? <p>Loading...</p> :  incomingLogs.map((log, id) => (
        <p key={id} className="log_text">[{log.severity}] : [{log.date}][{log.time}] =&gt; {log.message} </p> 
        ))}
      </div>
    </div>
  );
};

export default LiveLog;
