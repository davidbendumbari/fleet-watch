import { useEffect, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [error, setError] = useState(null);

  async function loadData() {
    try {
      const [devicesRes, alertsRes] = await Promise.all([
        fetch(`${API_URL}/devices`),
        fetch(`${API_URL}/alerts`),
      ]);
      setDevices(await devicesRes.json());
      setAlerts(await alertsRes.json());
      setError(null);
    } catch (err) {
      setError("Can't reach the API. Is it running?");
    }
  }

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const alertedDeviceIds = new Set(alerts.map((a) => a.device_id));

  return (
    <div className="app">
      <header className="header">
        <h1>SolarWatch</h1>
        <span className="subtitle">Fleet Monitoring</span>
      </header>

      {error && <div className="banner-error">{error}</div>}

      <section className="summary">
        <div className="summary-card">
          <span className="summary-value">{devices.length}</span>
          <span className="summary-label">Devices Reporting</span>
        </div>
        <div className="summary-card">
          <span className="summary-value alert-value">{alerts.length}</span>
          <span className="summary-label">Active Alerts</span>
        </div>
      </section>

      {alerts.length > 0 && (
        <section className="alerts">
          <h2>Alerts</h2>
          <ul className="alert-list">
            {alerts.map((a, i) => (
              <li key={i} className="alert-item">
                <span className="alert-device">{a.device_id}</span>
                <span className="alert-issue">{a.issue}</span>
                <span className="alert-value-inline">{a.value}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="devices">
        <h2>Fleet</h2>
        <table className="device-table">
          <thead>
            <tr>
              <th>Device</th>
              <th>Type</th>
              <th>Status</th>
              <th>Last Reading</th>
              <th>Updated</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((d) => (
              <tr key={d.device_id} className={alertedDeviceIds.has(d.device_id) ? "row-alert" : ""}>
                <td>{d.device_id}</td>
                <td>{d.type}</td>
                <td>
                  <span className={`status-dot ${alertedDeviceIds.has(d.device_id) ? "status-bad" : "status-ok"}`} />
                  {alertedDeviceIds.has(d.device_id) ? "Warning" : "Normal"}
                </td>
                <td>
                  {d.type === "solar"
                    ? `${d.data.output_kw} kW, ${d.data.temperature_c}°C`
                    : `${d.data.output_kw} kW, ${d.data.rpm} RPM`}
                </td>
                <td>{new Date(d.timestamp).toLocaleTimeString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

export default App;