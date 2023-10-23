import './App.css'
import MainDash from './components/MainDash/MainDash';
import Sidebar from './components/Sidebar/Sidebar';
import {
  BrowserRouter as Router,
  Switch,
  Routes,
  Route,
  Link,
  Navigate
} from "react-router-dom";
import AppUpload from './components/AppUpload/AppUpload';
import SignUp from './components/SignUp/SignUp';
import Login from './components/Login/Login';
import AppSchedule from './components/AppSchedule/AppSchedule';
import Logs from './components/Logs/Logs';
import SubsystemInstance from './components/Logs/SubsystemInstance';
import LiveLog from './components/Logs/LiveLog';
import DeveloperDocs from './components/DeveloperDocs/DeveloperDocs';
import SensorReg from './components/SensorReg/SensorReg';
function App() {
  const user = localStorage.getItem("userID");
  const type = localStorage.getItem("role");
  console.log("Here", user, type);

  return (
    <div className="">
      <div className=''>
        <Router>
          <Routes>
            <Route path="/signup" exact element={<SignUp />} />
            <Route path="/login" exact element={<Login />} />
            {user && type==='AppDeveloper' && <Route exact path='/dashboard' element={<div className='App'><div className='AppGlass'><Sidebar/><MainDash/></div></div>} />}
            {user && type==='AppDeveloper' && <Route exact path='/uploadapp' element={<div className='App'><div className='AppGlass'><Sidebar/><AppUpload/></div></div>} />}
            {user && type==='AppDeveloper' && <Route exact path='/sensor-reg' element={<div className='App'><div className='AppGlass'><Sidebar/></div></div>} />}
            {user && type==='AppDeveloper' && <Route exact path='/appschedule' element={<div className='App'><div className='AppGlass'><Sidebar/><AppSchedule/></div></div>} />}
            {user && type==='AppDeveloper' && <Route exact path='/developer-docs' element={<div className='App'><div className='AppGlass'><Sidebar/><DeveloperDocs/></div></div>} />}
            {user && type==='Admin' && <Route exact path='/sensor-reg' element={<div className='App'><div className='AppGlass'><Sidebar/><SensorReg/></div></div>} />}
            {user && type==='Admin' && <Route exact path='/logs' element={<div className='App'><div className='AppGlass'><Sidebar/><Logs/></div></div>} />}
            {user && type==='Admin' && <Route exact path='/logs/:subsystem' element={<div className='App'><div className='AppGlass'><Sidebar/><SubsystemInstance/></div></div>} />}
            {user && type==='Admin' && <Route exact path='/logs/:subsystem/:instance' element={<div className='App'><div className='AppGlass'><Sidebar/><LiveLog/></div></div>} />}
            <Route exact path='/' element={<Login />} />
          </Routes>
        </Router>
      </div>
    </div>
  );
}

export default App;
