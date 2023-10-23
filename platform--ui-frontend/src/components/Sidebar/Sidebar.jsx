import React, { useState } from 'react'
import './Sidebar.css'
import Logo from '../../imgs/logo1.png'
import {UilEstate} from "@iconscout/react-unicons"
import { Sidebardata, adminSidebardata, developerSidebardata } from '../../data/data'
import { Link } from 'react-router-dom'

const userRole = localStorage.getItem("role");
const Sidebar = () => {

    const [selected, setSelected] = useState(0)

    return (
        <div className='Sidebar'>
            <div className='logo'>
                <img src={Logo} alt="" />
                <span>
                    I<span>o</span>T Platform
                </span>
            </div>
            <div className='menu'>
                {userRole === 'AppDeveloper' ? developerSidebardata.map((item, index)=> {
                    return(
                        <div className={selected===index?'menuItem active': 'menuItem'}
                        key={index}
                        onClick={()=>setSelected(index)}
                        >
                            <item.icon />
                            <Link to={`/${item.link}`} style={{ textDecoration: 'none' }}>
                                <span>
                                    {item.heading}
                                </span>
                            </Link>
                        </div>
                    )
                })
                :
                adminSidebardata.map((item, index)=> {
                    return(
                        <div className={selected===index?'menuItem active': 'menuItem'}
                        key={index}
                        onClick={()=>setSelected(index)}
                        >
                            <item.icon />
                            <Link to={`/${item.link}`} style={{ textDecoration: 'none' }}>
                                <span>
                                    {item.heading}
                                </span>
                            </Link>
                        </div>
                    )
                })
            }

            </div>
        </div>
    )
};

export default Sidebar