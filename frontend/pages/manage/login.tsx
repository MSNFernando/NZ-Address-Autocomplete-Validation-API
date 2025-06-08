"use client";

import { useState } from "react";
import { useRouter } from "next/router";

export default function AdminLogin() {
  const [token, setToken] = useState("");
  const router = useRouter();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (token) {
      sessionStorage.setItem("admin_token", token);
      router.push("/manage");
    }
  };

  return (
    <div className="flex items-center justify-center h-screen">
      <form onSubmit={handleSubmit} className="p-8 bg-white rounded shadow w-full max-w-sm">
        <h1 className="text-xl font-bold mb-4">Admin Login</h1>
        <input
          type="password"
          placeholder="Admin Token"
          value={token}
          onChange={(e) => setToken(e.target.value)}
          className="w-full p-2 border rounded mb-4"
        />
        <button
          type="submit"
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
        >
          Enter
        </button>
      </form>
    </div>
  );
}
