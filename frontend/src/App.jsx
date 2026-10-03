

import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL;

function formatDateTime(value) {
  return new Date(value).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function App() {
  const [apiStatus, setApiStatus] = useState("checking");
  const [horizon, setHorizon] = useState(24);
  const [forecasts, setForecasts] = useState([]);
  const [savedForecasts, setSavedForecasts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    async function checkHealth() {
      try {
        const response = await fetch(`${API_URL}/health`);

        if (!response.ok) {
          throw new Error("Health check failed");
        }

        const data = await response.json();
        setApiStatus(data.status === "healthy" ? "online" : "offline");
      } catch {
        setApiStatus("offline");
      }
    }

    checkHealth();
  }, []);

  async function loadSavedForecasts() {
    try {
      const response = await fetch(`${API_URL}/forecasts?limit=100`);

      if (!response.ok) {
        throw new Error("Could not load saved forecasts.");
      }

      const data = await response.json();
      setSavedForecasts(data.forecasts || []);
    } catch (err) {
      console.error("Failed to load saved forecasts:", err);
    }
  }

  useEffect(() => {
    loadSavedForecasts();
  }, []);

  async function generateForecast(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/forecast`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          horizon: Number(horizon),
        }),
      });

      if (!response.ok) {
        const message = await response.text();

        throw new Error(
          `Forecast request failed (${response.status}): ${message}`
        );
      }

      const data = await response.json();

      if (!Array.isArray(data.forecasts)) {
        throw new Error("The API returned an unexpected response format.");
      }

      setForecasts(data.forecasts);
      setLastUpdated(new Date());

      await loadSavedForecasts();
    } catch (err) {
      setError(err.message || "Could not connect to the forecasting API.");
    } finally {
      setLoading(false);
    }
  }

  const latestForecast =
    forecasts.length > 0
      ? forecasts[forecasts.length - 1].forecast
      : null;

  const averageForecast =
    forecasts.length > 0
      ? forecasts.reduce((sum, item) => sum + item.forecast, 0) /
        forecasts.length
      : null;

  const chartData = forecasts.map((item) => ({
    time: formatDateTime(item.datetime),
    forecast: item.forecast,
  }));

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">⚡</div>

          <div>
            <h2>EnergyForecast</h2>
            <p>Demand intelligence</p>
          </div>
        </div>

        <nav className="navigation">
          <a href="#overview" className="nav-link active">
            <span>▦</span> Overview
          </a>

          <a href="#forecast" className="nav-link">
            <span>⌁</span> Forecasts
          </a>

          <a href="#history" className="nav-link">
            <span>◷</span> Results
          </a>
        </nav>

        <div className="sidebar-footer">
          <div
            className="status-dot"
            style={{
              background:
                apiStatus === "online"
                  ? "#10b981"
                  : apiStatus === "offline"
                  ? "#ef4444"
                  : "#f59e0b",
            }}
          />

          <span>
            API {apiStatus === "checking" ? "checking..." : apiStatus}
          </span>
        </div>
      </aside>

      <main className="main-content" id="overview">
        <header className="topbar">
          <div>
            <p className="eyebrow">ENERGY ANALYTICS</p>

            <h1>Demand Overview</h1>

            <p className="subtitle">
              Generate and inspect electricity demand forecasts.
            </p>
          </div>

          <div className="updated-label">
            <span
              className="status-dot"
              style={{
                background:
                  apiStatus === "online" ? "#10b981" : "#ef4444",
              }}
            />

            API {apiStatus}
          </div>
        </header>

        <section className="metrics-grid">
          <article className="metric-card">
            <div className="metric-heading">
              <span>Latest Forecast</span>
              <span className="metric-icon green">↗</span>
            </div>

            <h2>
              {latestForecast === null
                ? "—"
                : Math.round(latestForecast).toLocaleString()}

              <span> kW</span>
            </h2>

            <p className="metric-description">
              Last value in the generated forecast
            </p>
          </article>

          <article className="metric-card">
            <div className="metric-heading">
              <span>Average Forecast</span>
              <span className="metric-icon blue">◎</span>
            </div>

            <h2>
              {averageForecast === null
                ? "—"
                : Math.round(averageForecast).toLocaleString()}

              <span> kW</span>
            </h2>

            <p className="metric-description">
              Mean across generated forecast points
            </p>
          </article>

          <article className="metric-card">
            <div className="metric-heading">
              <span>Forecast Horizon</span>
              <span className="metric-icon purple">◷</span>
            </div>

            <h2>
              {forecasts.length || "—"} <span>hours</span>
            </h2>

            <p className="metric-description">
              {forecasts.length > 0
                ? "Points returned by the API"
                : "Generate a forecast to begin"}
            </p>
          </article>
        </section>

        <section className="history-card">
          <div className="section-heading">
            <div>
              <h2>Generate Forecast</h2>

              <p>Request predictions from your trained ML model.</p>
            </div>
          </div>

          <form onSubmit={generateForecast} className="forecast-form">
            <label htmlFor="horizon">Forecast horizon (hours)</label>

            <input
              id="horizon"
              type="number"
              min="1"
              max="168"
              step="1"
              value={horizon}
              onChange={(event) => setHorizon(event.target.value)}
              required
            />

            <button
              type="submit"
              disabled={loading || apiStatus === "offline"}
            >
              {loading ? "Generating..." : "Generate Forecast"}
            </button>
          </form>

          {error && (
            <div className="error-message" role="alert">
              {error}
            </div>
          )}

          {lastUpdated && !error && (
            <p className="metric-description request-time">
              Last generated: {lastUpdated.toLocaleString()}
            </p>
          )}
        </section>

        <section className="chart-card" id="forecast">
          <div className="section-heading">
            <div>
              <h2>Forecasted Electricity Demand</h2>

              <p>
                {forecasts.length > 0
                  ? "Predictions returned by your forecasting API"
                  : "Generate a forecast to display the results here"}
              </p>
            </div>

            <span className="chart-badge">
              {forecasts.length > 0 ? "Live API data" : "Awaiting data"}
            </span>
          </div>

          <div className="chart-container">
            {forecasts.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={chartData}
                  margin={{
                    top: 12,
                    right: 12,
                    left: 8,
                    bottom: 4,
                  }}
                >
                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#e8edf3"
                  />

                  <XAxis
                    dataKey="time"
                    tick={{
                      fill: "#718096",
                      fontSize: 11,
                    }}
                    axisLine={false}
                    tickLine={false}
                    minTickGap={25}
                  />

                  <YAxis
                    tick={{
                      fill: "#718096",
                      fontSize: 12,
                    }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(value) =>
                      `${Math.round(value / 1000)}k`
                    }
                    width={48}
                  />

                  <Tooltip
                    formatter={(value) =>
                      `${Number(value).toLocaleString(undefined, {
                        maximumFractionDigits: 2,
                      })} kW`
                    }
                  />

                  <Line
                    type="monotone"
                    dataKey="forecast"
                    name="Forecast demand"
                    stroke="#10b981"
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{ r: 5 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                <span className="empty-state-icon">⌁</span>

                <p>No forecast generated yet.</p>

                <span>
                  Use the form above to request predictions from the API.
                </span>
              </div>
            )}
          </div>
        </section>

        <section className="history-card" id="history">
          <div className="section-heading">
            <div>
              <h2>Saved Forecast History</h2>

              <p>
                Forecasts persisted in the SQLite database
              </p>
            </div>
          </div>

          {savedForecasts.length > 0 ? (
            <div className="table-wrapper">
              <table>
                <thead>
                  <tr>
                    <th>Forecast Time</th>
                    <th>Predicted Demand</th>
                    <th>Generated At</th>
                  </tr>
                </thead>

                <tbody>
                  {savedForecasts.map((item, index) => (
                    <tr
                      key={`${item.datetime}-${item.created_at}-${index}`}
                    >
                      <td>{formatDateTime(item.datetime)}</td>

                      <td>
                        {Number(item.forecast).toLocaleString(undefined, {
                          maximumFractionDigits: 2,
                        })}{" "}
                        kW
                      </td>

                      <td>{formatDateTime(item.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="empty-state table-empty">
              <p>No saved forecasts yet.</p>

              <span>
                Generated forecasts will be stored here automatically.
              </span>
            </div>
          )}
        </section>

        <footer className="page-footer">
          Energy Forecasting ML Project · FastAPI + React
        </footer>
      </main>
    </div>
  );
}

export default App;
