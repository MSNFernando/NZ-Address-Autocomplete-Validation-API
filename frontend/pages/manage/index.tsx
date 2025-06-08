"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/router";

interface UsageStats {
  [key: string]: string;
}

export default function AdminDashboard() {
  const router = useRouter();
  const [adminToken, setAdminToken] = useState<string | null>(null);
  const [usage, setUsage] = useState<UsageStats>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = sessionStorage.getItem("admin_token");
    if (!token) {
      router.push("/manage/login");
    } else {
      setAdminToken(token);
      fetch(`/api/admin/usage?admin_token=${token}`)
        .then(res => res.json())
        .then(data => {
          setUsage(data);
          setLoading(false);
        })
        .catch(() => {
          alert("Failed to load usage stats. Check your token or backend connection.");
          router.push("/manage/login");
        });
    }
  }, [router]);

  if (loading) return <p className="p-8">Loading...</p>;

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Admin Dashboard</h1>
      <h2 className="text-lg font-semibold mb-2">API Key Usage (today)</h2>
      <table className="table-auto w-full border border-gray-300">
        <thead>
          <tr className="bg-gray-100">
            <th className="text-left p-2 border">API Key</th>
            <th className="text-left p-2 border">Usage Count</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(usage).map(([key, value]) => (
            <tr key={key}>
              <td className="p-2 border text-sm break-all">{key}</td>
              <td className="p-2 border text-sm">{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
