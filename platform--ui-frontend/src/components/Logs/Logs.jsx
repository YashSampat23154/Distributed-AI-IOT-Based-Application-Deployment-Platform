import React from "react";
import { Subsystem_Names } from "../../data/data";
import "./Logs.css";
import { Link, NavLink, Navigate } from "react-router-dom";
import { Carousel } from 'antd';

const contentStyle = {
  height: '160px',
  color: '#fff',
  lineHeight: '160px',
  textAlign: 'center',
  background: '#364d79',
};

const Logs = () => {
  const onChange = (currentSlide) => {
    console.log(currentSlide);
  };
  return (
    <div style={{ marginTop: "50px" }}>
      <h2>Subsystems</h2>
      <div className="subsystem_container">
        {Subsystem_Names.map((subsystem, id) => (
          <Link
            style={{ textDecoration: "none" }}
            to={"/logs/" + subsystem.link}
            key={id}
          >
            <div className="logs_card" key={id}>
              <h2>{subsystem.name}</h2>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default Logs;
