import { useEffect } from "react";
import { useOrderStore } from "@/stores/order-store";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export function OrdersPage() {
  const { orders, loading, fetchOrders, markShipped, complete } = useOrderStore();
  const { user } = useAuthStore();

  useEffect(() => {
    fetchOrders();
  }, [fetchOrders]);

  const isBuyer = (order: { buyer_id: string }) => order.buyer_id === user?.id;
  const isSeller = (order: { seller_id: string }) => order.seller_id === user?.id;

  const handleShip = async (orderId: string) => {
    const num = window.prompt("Tracking number:");
    if (num) await markShipped(orderId, num, "FedEx");
  };

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">My Orders</h1>
      {loading && <p className="text-muted-foreground">Loading...</p>}
      {!loading && (
        <ul className="divide-y border rounded-lg overflow-hidden">
          {orders.map((order) => (
            <li key={order.id} className="p-4 flex flex-wrap items-center justify-between gap-2">
              <div>
                <p className="font-medium">Order #{order.id.slice(0, 8)} — Ð{order.amount}</p>
                <p className="text-sm text-muted-foreground">
                  {isBuyer(order) ? "Buying from" : "Selling to"} {isBuyer(order) ? order.seller_id : order.buyer_id}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm px-2 py-1 rounded bg-muted">{order.status}</span>
                {isSeller(order) && order.status === "PAID" && (
                  <Button size="sm" variant="outline" onClick={() => handleShip(order.id)}>Mark Shipped</Button>
                )}
                {isBuyer(order) && (order.status === "SHIPPED" || order.status === "DELIVERED") && (
                  <Button size="sm" onClick={() => complete(order.id)}>Confirm Receipt</Button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {!loading && orders.length === 0 && <p className="text-muted-foreground">No orders yet.</p>}
    </div>
  );
}
