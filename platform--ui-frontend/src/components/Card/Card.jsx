import React, { useState } from 'react'
import './Card.css'
import { AnimateSharedLayout } from 'framer-motion'
import { Statistic } from "antd";
import CountUp from 'react-countup';

export const Card = (props) => {
    const [expanded, setExpanded] = useState(false);
    const Png = props.png;
    // const numVal = props.value;
    const [value, setValue] = useState(props.value);
    const formatter = (value) => <CountUp end={value} separator="," />;
    console.log(value);
    return (
        <div className='CompactCard'
        style={{
            background: props.color.backGround,
            boxShadow: props.color.boxShadow
        }}>
            <div className='imglogo'>
                <Png size={90}/>
            </div>
            <div className='detail'>
                <span>{props.title}</span>
                <span><Statistic style={{ color: 'white' }} title="" value={props.value} precision={2} formatter={formatter} /></span>
            </div>
        </div>
    )
    // const Png = props.png;
    // return(
    //     <div className='CompactCard'
    //     style={{
    //         background: props.color.backGround,
    //         boxShadow: props.color.boxShadow
    //     }}>
    //         <div className='detail'>
    //             <Png />
    //             <span>${props.value}</span>
    //         </div>
    //     </div>
    // )
};


// function CompactCard ({param}) {
//     const Png = param.png;
//     return(
//         <div className='CompactCard'
//         style={{
//             background: param.color.backGround,
//             boxShadow: param.color.boxShadow
//         }}>
//             <div className='imglogo'>
//                 <Png size={90}/>
//             </div>
//             <div className='detail'>
//                 <span>{param.title}</span>
//                 <span>{param.value}</span>
//             </div>
//         </div>
//     )
// }

export default Card;