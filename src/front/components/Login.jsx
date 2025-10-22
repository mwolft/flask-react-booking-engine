import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";

export const Login = () => {
  const { dispatch } = useGlobalReducer();
  const navigate = useNavigate();

  const [isRegister, setIsRegister] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: ""
  });

  const backendUrl = import.meta.env.VITE_BACKEND_URL;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      if (isRegister) {
        // 🔹 Registro
        const res = await fetch(`${backendUrl}/api/users/register`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(formData)
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.error || "Error al registrarse");

        // 🔹 Auto-login tras registro
        await handleLogin(formData.email, formData.password);
      } else {
        // 🔹 Login normal
        await handleLogin(formData.email, formData.password);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleLogin = async (email, password) => {
    const res = await fetch(`${backendUrl}/api/users/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || "Error al iniciar sesión");

    localStorage.setItem("token", data.token);
    dispatch({ type: "set_user", payload: { user: data.user, token: data.token } });
    navigate("/");
  };

  return (
    <div className="home-container">
      <h1 className="title">{isRegister ? "Crear cuenta" : "Iniciar sesión"}</h1>
      <form className="booking-form" onSubmit={handleSubmit}>
        {isRegister && (
          <>
            <div className="form-group">
              <label>Nombre</label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Apellidos</label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
              />
            </div>
          </>
        )}

        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label>Contraseña</label>
          <input
            type="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>

        <button type="submit" className="submit-btn">
          {isRegister ? "Registrarme" : "Entrar"}
        </button>

        {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}
      </form>

      <p style={{ marginTop: "1rem" }}>
        {isRegister ? (
          <>
            ¿Ya tienes cuenta?{" "}
            <button
              style={{ color: "#F4B858", background: "none", border: "none", cursor: "pointer" }}
              onClick={() => setIsRegister(false)}
            >
              Inicia sesión
            </button>
          </>
        ) : (
          <>
            ¿No tienes cuenta?{" "}
            <button
              style={{ color: "#F4B858", background: "none", border: "none", cursor: "pointer" }}
              onClick={() => setIsRegister(true)}
            >
              Regístrate aquí
            </button>
          </>
        )}
      </p>
    </div>
  );
};

