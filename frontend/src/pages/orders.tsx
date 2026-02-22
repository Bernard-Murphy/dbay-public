import { useEffect } from "react";
import { useOrderStore } from "@/stores/order-store";
import { useAuthStore } from "@/stores/auth-store";
import { Button } from "@/components/ui/button";
import { DogeIcon } from "@/components/doge-icon";
import { formatDogeWithUsd } from "@/lib/format";
import { useDogeRateStore } from "@/stores/doge-rate-store";
import { motion, AnimatePresence } from "framer-motion";
import { normalize, fade_out_scale_1, transition_fast } from "@/lib/transitions";
import Spinner from "@/components/ui/spinner";

export function OrdersPage() {
  const { orders, loading, fetchOrders, markShipped, complete } = useOrderStore();
  const { user } = useAuthStore();
  const dogeRate = useDogeRateStore((s) => s.rate);

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
      <AnimatePresence mode="wait">
        {!loading && (
          <motion.ul initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="divide-y border rounded-lg overflow-hidden">
            {orders.map((order) => (
              <li key={order.id} className="p-4 flex flex-wrap items-center justify-between gap-2">
                <div>
                  <p className="font-medium flex items-center gap-1">
                    Order #{order.id.slice(0, 8)} — <DogeIcon size={16} />
                    {formatDogeWithUsd(Number(order.amount), dogeRate)}
                  </p>
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
          </motion.ul>
        )}
        {loading && <motion.div key="loading" initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="p-4 flex items-center justify-center"><Spinner size="sm" /></motion.div>}
        {!loading && orders.length === 0 && <motion.p key="no-orders" initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="text-muted-foreground mt-2">No orders yet.</motion.p>}
      </AnimatePresence>
    </div>
  );
}
