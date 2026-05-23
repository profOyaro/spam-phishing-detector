CREATE TABLE detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    subject TEXT,
    sender TEXT,
    label TEXT NOT NULL,
    risk_score REAL NOT NULL,
    risk_level TEXT NOT NULL,
    details_json TEXT NOT NULL
);

CREATE INDEX idx_detections_created_at ON detections(created_at);
CREATE INDEX idx_detections_risk_level ON detections(risk_level);
