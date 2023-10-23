import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { deployer_instance } from "../../data/data";
import axios from "axios";

const SubsystemInstance = () => {
  const { subsystem } = useParams();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState([]);

  const fetchData = () => {
    return axios
      .get("http://localhost:5000/get_subsystem_instances?subsystem_name=" + subsystem)
      .then((response) => {
        setData(response.data.instances);
        console.log(response.data.instances);
        setLoading(false);
      })
      .catch((error) => console.log(error));
  };
  useEffect(() => {
    setLoading(true);
    // setData(deployer_instance);
    fetchData();
  }, []);

  return (
    <div style={{ overflowY: "scroll", width: "100%" }}>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div>
          <h2>Subsystem: {subsystem}</h2>
          {data.length == 0 && <p>No instances of {subsystem} are running yet ...</p>}
          {data.map((ins, id) => (
            <a
              style={{ textDecoration: "none" }}
              href={"/logs/" + subsystem + "/" + ins.instance_name}
              key={id}
              target="_blank"
            >
              <div className="instance">
                <h3>{ins.instance_name}</h3>
              </div>
            </a>
          ))}
        </div>
      )}
    </div>
  );
};

export default SubsystemInstance;
