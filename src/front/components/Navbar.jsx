import React, { useState } from "react";
import { Link } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer.jsx";

export const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { store, dispatch } = useGlobalReducer();

  const toggleMenu = () => setIsMenuOpen(!isMenuOpen);

  const handleLogout = () => {
    dispatch({ type: "logout_user" });
  };

  return (
    <nav className="main-nav">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          <span>Booking System Hotel</span>
        </Link>

        <button
          className="hamburger-button"
          onClick={toggleMenu}
          aria-expanded={isMenuOpen}
          aria-label="Toggle navigation"
        >
          &#9776;
        </button>

        <div className={`nav-links ${isMenuOpen ? "is-open" : ""}`}>
          {store.user ? (
            <>
              <span className="user-label">
                {store.user.first_name || store.user.email}
              </span>
              <button className="nav-button" onClick={handleLogout}>
                Cerrar sesión
              </button>
            </>
          ) : (
            <Link to="/login">
              <button className="nav-button">Login</button>
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
};
