import { useState, useEffect } from "react";
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import { Alert, message } from 'antd';
import styles from "./loginstyles.module.css";

const Login = () => {
	const [data, setData] = useState({ userID: "", password: "", role: "" });
	const [error, setError] = useState("");
	const navigate = useNavigate();

	const type = ["AppDeveloper", "Admin"];
	const [selectedtype, setSelected] = useState(type[0]);
	const [errorMessageApi, errorContextHolder] = message.useMessage();

	const handleChange = ({ currentTarget: input }) => {
		setData({ ...data, [input.name]: input.value });
	};

	const info = (msg) => {
		errorMessageApi.info(msg);
	};

	const handleSubmit = async (e) => {
		e.preventDefault();
		try {
			// const url = "http://20.163.121.196:8001/login";
			// data.role = selectedtype;
			// console.log("Before Login: ", data);
			// // alert("Before Login " + data);
			// axios.post(url, data, {
			// 	headers: {
			// 		'Content-Type': 'application/json'
			// 	}
			// }).then(function (response) {
			// 	console.log(response);
			// 	localStorage.setItem("userID", data.userID);
			// 	localStorage.setItem("role", data.role);
			// 	navigate("/dashboard");
			// }).catch(function (error) {
			// 	console.log(error);
			// 	info('Invalid username or password!');
			// });
			// console.log(response);
			data.role = selectedtype;
			localStorage.setItem("userID", data.userID);
			localStorage.setItem("role", data.role);
			console.log('Role is:', localStorage.getItem("role"));
			console.log('Data is:', data);
			if(data.role == 'AppDeveloper')
				navigate("/dashboard");
			else navigate("/logs");
		} catch (error) {
			console.log("Here", error);
			if (
				error.response &&
				error.response.status >= 400 &&
				error.response.status <= 500
			) {
				setError(error.response.data.message);
				info('Internal Server Error!');
			}
		}
		// localStorage.setItem("token", "123");
		// localStorage.setItem("userID", "sid");
		// navigate("/dashboard");
	};

	return (
		<div>
			{errorContextHolder}
			<h2 style={{ "marginLeft": "40rem" }}>IoT Platform</h2>
			<div className={styles.login_container}>
				<div className={styles.login_form_container}>
					<div className={styles.left}>
						<form className={styles.form_container} onSubmit={handleSubmit}>
							<h1>Login to Your Account</h1>
							{/* <input
							type="text"
                            placeholder="RollNumber"
                            onChange={handleChange}
                            value={data.rollno}
						/> */}
							<input
								type="text"
								placeholder="userID"
								name="userID"
								onChange={handleChange}
								value={data.userID}
								required
								className={styles.input}
							/>
							<input
								type="Password"
								placeholder="Password"
								name="password"
								onChange={handleChange}
								value={data.password}
								required
								className={styles.input}
							/>
							{/* <input
							type="Role"
							placeholder="Role(Student/TA)"
							name="role"
							onChange={handleChange}
							value={data.role}
							required
							className={styles.input}
						/> */}
							<select className={styles.input} onChange={e => setSelected(e.target.value)}>
								{type.map((value) => (
									<option value={value} key={value}>
										{value}
									</option>
								))}
							</select>
							{error && <div className={styles.error_msg}>{error}</div>}
							<button type="submit" className={styles.green_btn}>
								Sign In
							</button>
						</form>
					</div>
					<div className={styles.right}>
						<h1>New Here ?</h1>
						<Link to="/signup">
							<button type="button" className={styles.white_btn}>
								Sign Up
							</button>
						</Link>
					</div>
				</div>
			</div>
		</div>
	);
};

export default Login;