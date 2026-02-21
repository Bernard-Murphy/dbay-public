import { useEffect, useState } from "react";
import { api } from "@/services/api";

interface Dispute {
  id: string;
  reason: string;
  status: string;
}

export function AdminDashboardPage() {
  const [disputes, setDisputes] = useState<Dispute[]>([]);

  useEffect(() => {
    api.get("/order/disputes/").then((res) => setDisputes(Array.isArray(res.data) ? res.data : [])).catch(() => setDisputes([]));
  }, []);

  return (
    <div className="container max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="rounded-lg border bg-card p-6">
          <dt className="text-sm text-muted-foreground">Total Disputes</dt>
          <dd className="text-3xl font-semibold mt-1">{disputes.length}</dd>
        </div>
      </div>
      <div className="rounded-lg border overflow-hidden">
        <h2 className="font-semibold p-4 border-b">Recent Disputes</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-left p-3">ID</th>
              <th className="text-left p-3">Reason</th>
              <th className="text-left p-3">Status</th>
              <th className="text-right p-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {disputes.map((d) => (
              <tr key={d.id} className="border-b">
                <td className="p-3">{d.id}</td>
                <td className="p-3">{d.reason}</td>
                <td className="p-3">{d.status}</td>
                <td className="p-3 text-right"><a href="#" className="text-primary hover:underline">View</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
