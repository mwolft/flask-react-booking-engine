import React, { useState } from "react";

export const Home = () => {
  const [form, setForm] = useState({
    checkIn: "",
    checkOut: "",
    adults: 1,
    children: 0,
    roomType: ""
  });

  const [availability, setAvailability] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const base = import.meta.env.VITE_BACKEND_URL;
      if (!base) throw new Error("VITE_BACKEND_URL no está definida");

      const params = new URLSearchParams({
        check_in: form.checkIn,
        check_out: form.checkOut,
        room_type: form.roomType
      });

      const res = await fetch(`${base}/api/hotel/availability?${params.toString()}`);
      if (!res.ok) throw new Error("Error al obtener disponibilidad");
      const data = await res.json();
      setAvailability(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Error inesperado");
      setAvailability([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="home-container">
      <h1 className="title">Reserva tu estancia</h1>
      <form className="booking-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Entrada</label>
          <input type="date" name="checkIn" value={form.checkIn} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Salida</label>
          <input type="date" name="checkOut" value={form.checkOut} onChange={handleChange} required />
        </div>
        <div className="form-group">
          <label>Adultos</label>
          <input type="number" name="adults" value={form.adults} onChange={handleChange} min="1" />
        </div>
        <div className="form-group">
          <label>Niños</label>
          <input type="number" name="children" value={form.children} onChange={handleChange} min="0" />
        </div>
        <div className="form-group">
          <label>Habitación</label>
          <select name="roomType" value={form.roomType} onChange={handleChange} required>
            <option value="">Selecciona tipo</option>
            <option value="doble">Doble</option>
            <option value="suite">Suite</option>
            <option value="familiar">Familiar</option>
          </select>
        </div>
        <button type="submit" className="submit-btn">{loading ? "Buscando..." : "Buscar disponibilidad"}</button>
      </form>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      {availability.length > 0 && (
        <div style={{ marginTop: "2rem", width: "100%", maxWidth: 900 }}>
          <h3>Resultados</h3>
          <ul>
            {availability.map((a) => (
              <li key={a.id}>
                {a.date} — {a.room_number || "—"} {a.room_type_name ? `(${a.room_type_name})` : ""} — {a.is_available ? "Libre" : "Ocupada"}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
