import React, { useState } from "react";
import { Link } from "react-router-dom";

export const Navbar = () => {
    const [isMenuOpen, setIsMenuOpen] = useState(false);

    const toggleMenu = () => {
        setIsMenuOpen(!isMenuOpen);
    };

    return (
        <nav className="main-nav">
            <div className="nav-container">
                {/* 1. Nombre/Logo a la Izquierda */}
                <Link to="/" className="nav-logo">
                    <span>Booking System Hotel</span>
                </Link>

                {/* 2. Botón de Hamburguesa (Solo visible en móviles) */}
                <button 
                    className="hamburger-button" 
                    onClick={toggleMenu}
                    aria-expanded={isMenuOpen}
                    aria-label="Toggle navigation"
                >
                    {/* Icono de hamburguesa simple */}
                    &#9776; 
                </button>

                {/* 3. Contenido del Menú (Visible en desktop, condicional en móvil) */}
                <div className={`nav-links ${isMenuOpen ? "is-open" : ""}`}>
                    <Link to="/login">
                        <button className="nav-button">Login</button>
                    </Link>
                </div>
            </div>
        </nav>
    );
};