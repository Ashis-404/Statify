import { useEffect, useState } from 'react';
import axios from 'axios';

interface SystemStatus {
  status: string;
  total_servers: number;
  down_servers: number;
  warning_servers: number;
}

interface Server {
  id: number;
  name: string;
  url: string;
  last_status: string;
  last_check_time: string;
  uptime_24h: number;
}

const API_URL = 'http://localhost:5000/api';

function App() {
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [servers, setServers] = useState<Server[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statusRes, serversRes] = await Promise.all([
        axios.get(`${API_URL}/status`),
        axios.get(`${API_URL}/servers`)
      ]);
      setStatus(statusRes.data);
      setServers(serversRes.data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err: any) {
      console.error(err);
      setError('Failed to connect to the monitoring API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    if (status.includes('Operational')) return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    if (status.includes('Outage')) return 'bg-rose-100 text-rose-800 border-rose-200';
    if (status.includes('Warning') || status.includes('Degraded')) return 'bg-amber-100 text-amber-800 border-amber-200';
    return 'bg-gray-100 text-gray-800 border-gray-200';
  };

  const getServerBadgeColor = (status: string) => {
    if (status === 'UP') return 'bg-emerald-500';
    if (status === 'DOWN') return 'bg-rose-500';
    if (status === 'WARNING') return 'bg-amber-500';
    return 'bg-gray-500';
  };

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">System Status</h1>
          <p className="text-gray-500">Live monitoring dashboard updated every 30s</p>
        </header>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded shadow-sm">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          </div>
        )}

        {!error && status && (
          <div className={`rounded-lg border p-6 mb-8 shadow-sm flex items-center justify-between ${getStatusColor(status.status)}`}>
            <div>
              <h2 className="text-2xl font-semibold">{status.status}</h2>
              <p className="text-sm mt-1 opacity-80">
                {status.total_servers} services monitored • {status.down_servers} down
              </p>
            </div>
            <div className="text-right">
              <span className="text-sm opacity-70">Last updated</span>
              <p className="font-medium">{lastUpdated.toLocaleTimeString()}</p>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200 bg-gray-50 flex justify-between items-center">
            <h3 className="text-lg font-medium text-gray-900">Monitored Services</h3>
            {loading && <span className="text-xs text-gray-500 animate-pulse">Refreshing...</span>}
          </div>
          <ul className="divide-y divide-gray-200">
            {servers.map((server) => (
              <li key={server.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    <span className={`h-3 w-3 rounded-full mr-4 ${getServerBadgeColor(server.last_status)}`}></span>
                    <div>
                      <h4 className="text-lg font-medium text-gray-900">{server.name}</h4>
                      <a href={server.url} target="_blank" rel="noreferrer" className="text-sm text-blue-600 hover:underline">
                        {server.url}
                      </a>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-gray-900">
                      24h Uptime: <span className={server.uptime_24h > 99 ? 'text-green-600' : 'text-amber-600'}>{server.uptime_24h}%</span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Last check: {server.last_check_time ? new Date(server.last_check_time + 'Z').toLocaleTimeString() : 'Never'}
                    </p>
                  </div>
                </div>
              </li>
            ))}
            {servers.length === 0 && !loading && !error && (
              <li className="p-6 text-center text-gray-500">No servers configured.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default App;