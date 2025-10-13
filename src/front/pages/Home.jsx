import React, { useState } from "react"

export const Home = () => {
	const [form, setForm] = useState({
		checkIn: "",
		checkOut: "",
		adults: 1,
		children: 0,
		roomType: ""
	})

	const handleChange = e => {
		setForm({ ...form, [e.target.name]: e.target.value })
	}

	const handleSubmit = e => {
		e.preventDefault()
		console.log(form)
	}

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
				<button type="submit" className="submit-btn">Buscar disponibilidad</button>
			</form>
		</div>
	)
}
