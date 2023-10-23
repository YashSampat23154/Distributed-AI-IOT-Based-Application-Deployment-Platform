import React, {useState} from 'react'
import axios from "axios";
import { Link, useNavigate } from "react-router-dom";
import styles from "./styles.module.css";

const SignUp = () => {
    const [data, setData] = useState({
        firstname: "",
        lastname: "",
        userID: "",
        password: ""
    });
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const type = ["AppDeveloper", "Admin"];
    const [selectedtype, setSelected] = useState(type[0]);

    const handleChange = ({ currentTarget: input }) => {
        setData({ ...data, [input.name]: input.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const url = "http://20.163.121.196:8001/register";
            // data.role = selectedtype;
            console.log(data);
            const { data: res } = await axios.post(url, data);
            console.log("Here", data);
			console.log("Yo", res);
            navigate("/login");
        } catch (error) {
            console.log("Error:", error);
            if (
                error.response &&
                error.response.status >= 400 &&
                error.response.status <= 500
            ) {
                setError(error.response.data.message);
            }
        }
    };

    return (
        <div className={styles.signup_container}>
            <div className={styles.signup_form_container}>
                <div className={styles.left}>
                    <h1>Welcome Back</h1>
                    <Link to="/login">
                        <button type="button" className={styles.white_btn}>
                            Sign in
                        </button>
                    </Link>
                </div>
                <div className={styles.right}>
                    <form className={styles.form_container} onSubmit={handleSubmit}>
                        <h1>Create Account</h1>
                        <input
                            type="firstname"
                            placeholder="First name"
                            name="firstname"
                            onChange={handleChange}
                            value={data.firstname}
                            required
                            className={styles.input}
                        />
                        <input
                            type="lastname"
                            placeholder="Last name"
                            name="lastname"
                            onChange={handleChange}
                            value={data.lastname}
                            required
                            className={styles.input}
                        />
                        <input
                            type="text"
                            placeholder="User ID/Email ID"
                            name="userID"
                            onChange={handleChange}
                            value={data.userID}
                            required
                            className={styles.input}
                        />
                        <input
                            type="password"
                            placeholder="Password"
                            name="password"
                            onChange={handleChange}
                            value={data.password}
                            required
                            className={styles.input}
                        />
                        {error && <div className={styles.error_msg}>{error}</div>}
                        <button type="submit" className={styles.green_btn} onClick={handleSubmit}>
                            Sign Up
                        </button>
                    </form>
                </div>
            </div>
        </div>
    );
}

export default SignUp
