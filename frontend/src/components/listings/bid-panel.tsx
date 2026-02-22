import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuctionStore } from "@/stores/auction-store";
import type { Listing } from "@/types";
import { DogeIcon } from "@/components/doge-icon";
import { formatDogeWithUsd } from "@/lib/format";
import { useDogeRateStore } from "@/stores/doge-rate-store";

interface BidPanelProps {
  listing: Listing;
}

export function BidPanel({ listing }: BidPanelProps) {
  const [amount, setAmount] = useState("");
  const { placeBid, loading, error } = useAuctionStore();
  const dogeRate = useDogeRateStore((s) => s.rate);
  const minBid = (listing.current_price || 0) + (listing.current_price >= 100 ? 5 : 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = Math.round(parseFloat(amount));
    if (!Number.isNaN(value) && value >= minBid) {
      placeBid(listing.id, value);
      setAmount("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <p className="text-sm text-muted-foreground flex items-center gap-1">
        Minimum bid: <DogeIcon size={14} />
        {formatDogeWithUsd(minBid, dogeRate)}
      </p>
      <div className="flex gap-2 pr-2">
        <Input
          type="number"
          min={minBid}
          step={1}
          placeholder="Your bid"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <Button type="submit" bouncyClasses="pr-4" disabled={loading}>Place Bid</Button>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </form >
  );
}
