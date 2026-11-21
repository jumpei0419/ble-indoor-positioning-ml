CREATE TABLE IF NOT EXISTS rssi_samples (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(64) NOT NULL,
    method_mode ENUM('fp_ml', 'hybrid_ml', 'proximity') NOT NULL,
    grid_row TINYINT NOT NULL,
    grid_col TINYINT NOT NULL,
    sample_idx SMALLINT NOT NULL,
    receiver_id VARCHAR(32) NOT NULL,
    source_type ENUM('target', 'dummy') NOT NULL,
    beacon_id VARCHAR(32) NOT NULL,
    rssi INT NOT NULL,
    measured_at TIMESTAMP(3) DEFAULT CURRENT_TIMESTAMP(3),
    INDEX idx_session_grid (session_id, grid_row, grid_col)
);