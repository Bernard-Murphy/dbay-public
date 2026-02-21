import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useAuctionStore } from "@/stores/auction-store";
import type { Listing } from "@/types";

interface BidPanelProps {
  listing: Listing;
}

export function BidPanel({ listing }: BidPanelProps) {
  const [amount, setAmount] = useState("");
  const { placeBid, loading, error } = useAuctionStore();
  const minBid = (listing.current_price || 0) + (listing.current_price >= 100 ? 5 : 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const value = parseFloat(amount);
    if (!Number.isNaN(value) && value >= minBid) {
      placeBid(listing.id, value);
      setAmount("");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-2">
      <p className="text-sm text-muted-foreground">Minimum bid: Ð{minBid}</p>
      <div className="flex gap-2">
        <Input
          type="number"
          min={minBid}
          step="0.01"
          placeholder="Your bid"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <Button type="submit" disabled={loading}>Place Bid</Button>
      </div>
      {error && <p className="text-sm text-destructive">{error}</p>}
    </form>
  );
}
