import React from "react";
import { Row, Col, Card, Button } from "react-bootstrap";
import Skeleton from "react-loading-skeleton";

export const AvailabilityResults = ({ results, loading, hasSearched }) => {
  if (loading) {
    return (
      <Row className="mt-5">
        {[...Array(3)].map((_, i) => (
          <Col md={12} key={i}>
            <Card className="mb-4 shadow-sm">
              <Skeleton height={200} />
            </Card>
          </Col>
        ))}
      </Row>
    );
  }

  if (hasSearched && !loading && results.length === 0) {
    return (
      <p className="mt-4 text-center">
        No hay disponibilidad para las fechas seleccionadas.
      </p>
    );
  }

  // 🔹 Agrupar por tipo de habitación
  const grouped = results.reduce((acc, room) => {
    const typeId = room.room_type?.id || room.room_type_id;
    if (!acc[typeId]) {
      acc[typeId] = {
        ...room.room_type,
        available_count: 0,
      };
    }
    acc[typeId].available_count += 1;
    return acc;
  }, {});

  const roomTypes = Object.values(grouped);

  return (
    <div className="mt-5 availability-list">
      {roomTypes.map((type) => (
        <Card key={type.id} className="mb-4 shadow-sm roomtype-card">
          <Row className="g-0 align-items-center">
            <Col md={4}>
              <Card.Img
                src={type.image_url || "/default-room.jpg"}
                alt={type.name}
                className="roomtype-image"
              />
            </Col>
            <Col md={8}>
              <Card.Body>
                <Card.Title>{type.name}</Card.Title>
                <Card.Text className="text-muted">{type.description}</Card.Text>

                <div className="d-flex justify-content-between align-items-center mt-3">
                  <div>
                    <strong>{type.base_price.toFixed(2)} € / noche</strong>
                    <div className="text-secondary small">
                      {type.available_count} disponibles
                    </div>
                  </div>
                  <Button variant="primary" size="md">
                    Reservar
                  </Button>
                </div>
              </Card.Body>
            </Col>
          </Row>
        </Card>
      ))}
    </div>
  );
};
