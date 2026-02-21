import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useListingStore } from "@/stores/listing-store";
import type { Listing } from "@/types";

const CONDITIONS = ["NEW", "LIKE_NEW", "GOOD", "FAIR", "POOR"] as const;
const TYPES = ["AUCTION", "BUY_IT_NOW", "BOTH"] as const;

export function CreateListingPage() {
  const navigate = useNavigate();
  const { createListing, error: storeError } = useListingStore();
  const [form, setForm] = useState<Partial<Listing>>({
    title: "",
    description: "",
    condition: "NEW",
    listing_type: "AUCTION",
    starting_price: 0,
    buy_it_now_price: 0,
    reserve_price: 0,
    quantity: 1,
    shipping_cost: 0,
    shipping_from_country: "US",
  });
  const [images, setImages] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const created = await createListing(form, images);
      navigate(`/listings/${created.id}`);
    } catch {
      // error in store
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Create a Listing</h1>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <Label htmlFor="title">Title</Label>
          <Input
            id="title"
            value={form.title ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            required
          />
        </div>
        <div>
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={form.description ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="condition">Condition</Label>
            <select
              id="condition"
              value={form.condition ?? "NEW"}
              onChange={(e) => setForm((f) => ({ ...f, condition: e.target.value as Listing["condition"] }))}
              className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {CONDITIONS.map((c) => (
                <option key={c} value={c}>{c.replace("_", " ")}</option>
              ))}
            </select>
          </div>
          <div>
            <Label htmlFor="listing_type">Type</Label>
            <select
              id="listing_type"
              value={form.listing_type ?? "AUCTION"}
              onChange={(e) => setForm((f) => ({ ...f, listing_type: e.target.value as Listing["listing_type"] }))}
              className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            >
              {TYPES.map((t) => (
                <option key={t} value={t}>{t.replace("_", " ")}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="starting_price">Starting Price (Ð)</Label>
            <Input
              id="starting_price"
              type="number"
              min={0}
              step={0.01}
              value={form.starting_price ?? 0}
              onChange={(e) => setForm((f) => ({ ...f, starting_price: parseFloat(e.target.value) || 0 }))}
            />
          </div>
          <div>
            <Label htmlFor="buy_it_now_price">Buy It Now (Ð)</Label>
            <Input
              id="buy_it_now_price"
              type="number"
              min={0}
              step={0.01}
              value={form.buy_it_now_price ?? 0}
              onChange={(e) => setForm((f) => ({ ...f, buy_it_now_price: parseFloat(e.target.value) || 0 }))}
            />
          </div>
        </div>
        <div>
          <Label>Images</Label>
          <input
            type="file"
            multiple
            accept="image/*"
            className="mt-1 block w-full text-sm"
            onChange={(e) => setImages(Array.from(e.target.files ?? []))}
          />
        </div>
        {storeError && <p className="text-sm text-destructive">{storeError}</p>}
        <div className="flex gap-2">
          <Button type="submit" disabled={loading}>{loading ? "Creating..." : "Create Listing"}</Button>
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>Cancel</Button>
        </div>
      </form>
    </div>
  );
}
