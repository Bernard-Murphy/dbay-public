import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuctionStore } from "@/stores/auction-store";
import type { Listing } from "@/types";
import { DogeIcon } from "@/components/doge-icon";
import { formatDogeWithUsd } from "@/lib/format";
import { useDogeRateStore } from "@/stores/doge-rate-store";
import { PriceInput } from "@/components/price-input";
import { toast } from "sonner";

interface BidPanelProps {
  listing: Listing;
  onBidSuccess?: () => void;
}

export function BidPanel({ listing, onBidSuccess }: BidPanelProps) {
  const minBid = (listing.current_price || 0) + (listing.current_price >= 100 ? 5 : 1);
  const [amount, setAmount] = useState(minBid);
  const { placeBid, loading } = useAuctionStore();
  const dogeRate = useDogeRateStore((s) => s.rate);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const value = Math.round(Number(amount));
    if (Number.isNaN(value) || value < minBid) return;
    try {
      await placeBid(listing.id, value);
      setAmount(minBid);
      onBidSuccess?.();
      toast.success("Bid placed.");
    } catch {
      toast.error("Failed to place bid.");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <p className="text-sm text-muted-foreground flex items-center gap-1">
        Minimum bid: <DogeIcon size={14} />
        {formatDogeWithUsd(minBid, dogeRate)}
      </p>
      <PriceInput
        id="bid-amount"
        label="Your bid"
        value={amount}
        onChange={setAmount}
      />
      <div style={{ width: 'max-content' }}>
        <Button type="submit" disabled={loading}>Place Bid</Button>
      </div>
    </form>
  );
}
