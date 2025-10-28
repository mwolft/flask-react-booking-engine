import React, { useState } from "react";
import { AvailabilityResults } from "../components/AvailabilityResults.jsx";
import { Container, Row, Col, Form, Button, Alert } from "react-bootstrap";

export const Home = () => {
  const [form, setForm] = useState({
    checkIn: "",
    checkOut: "",
    adults: 1,
    children: 0,
  });

  const [availability, setAvailability] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false); // ✅ nuevo estado

  const base = import.meta.env.VITE_BACKEND_URL;

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setHasSearched(true); // ✅ activa el flag cuando se busca

    try {
      const params = new URLSearchParams({
        checkin: form.checkIn,
        checkout: form.checkOut,
      });

      const res = await fetch(
        `${base}/api/hotel/availability/search?${params.toString()}`
      );
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
    <Container style={{ marginTop: "70px" }}>
      <h1 className="text-center mb-4">Reserva tu estancia</h1>

      <Form
        onSubmit={handleSubmit}
        className="p-3 border rounded bg-light shadow-sm"
      >
        <Row className="g-3 align-items-end">
          <Col md={3}>
            <Form.Label>Entrada</Form.Label>
            <Form.Control
              type="date"
              name="checkIn"
              value={form.checkIn}
              onChange={handleChange}
              required
            />
          </Col>

          <Col md={3}>
            <Form.Label>Salida</Form.Label>
            <Form.Control
              type="date"
              name="checkOut"
              value={form.checkOut}
              onChange={handleChange}
              required
            />
          </Col>

          <Col md={2}>
            <Form.Label>Adultos</Form.Label>
            <Form.Control
              type="number"
              name="adults"
              value={form.adults}
              onChange={handleChange}
              min="1"
            />
          </Col>

          <Col md={2}>
            <Form.Label>Niños</Form.Label>
            <Form.Control
              type="number"
              name="children"
              value={form.children}
              onChange={handleChange}
              min="0"
            />
          </Col>

          <Col md={2}>
            <Button type="submit" variant="primary" className="w-100">
              {loading ? "Buscando..." : "Buscar"}
            </Button>
          </Col>
        </Row>
      </Form>

      {error && (
        <Alert variant="danger" className="mt-3">
          {error}
        </Alert>
      )}

      {/* ✅ pasamos hasSearched al componente */}
      <AvailabilityResults
        results={availability}
        loading={loading}
        hasSearched={hasSearched}
      />
    </Container>
  );
};
