import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PriceInput } from "@/components/price-input";
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
  const [files, setFiles] = useState<File[]>([]);
  const [fileError, setFileError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const MAX_VIDEO_BYTES = 100 * 1024 * 1024; // 100MB

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const chosen = Array.from(e.target.files ?? []);
    const err = chosen.find((f) => f.type.startsWith("video/") && f.size > MAX_VIDEO_BYTES);
    if (err) {
      setFileError(`Video "${err.name}" is over 100MB. Max size for videos is 100MB.`);
      return;
    }
    setFileError("");
    setFiles((prev) => [...prev, ...chosen]);
    e.target.value = "";
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const created = await createListing(form, files);
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
          <PriceInput
            id="starting_price"
            label="Starting Price"
            value={form.starting_price ?? 0}
            onChange={(doge) => setForm((f) => ({ ...f, starting_price: doge }))}
          />
          <PriceInput
            id="buy_it_now_price"
            label="Buy It Now"
            value={form.buy_it_now_price ?? 0}
            onChange={(doge) => setForm((f) => ({ ...f, buy_it_now_price: doge }))}
          />
        </div>
        <PriceInput
          id="shipping_cost"
          label="Shipping Cost"
          value={form.shipping_cost ?? 0}
          onChange={(doge) => setForm((f) => ({ ...f, shipping_cost: doge }))}
        />
        <div>
          <Label>Photos &amp; Videos</Label>
          <p className="text-xs text-muted-foreground mb-1">Multiple files allowed. Videos max 100MB.</p>
          <input
            type="file"
            multiple
            accept="image/*,video/*"
            className="mt-1 block w-full text-sm"
            onChange={handleFileChange}
          />
          {fileError && <p className="text-sm text-destructive mt-1">{fileError}</p>}
          {files.length > 0 && (
            <ul className="mt-2 space-y-1 text-sm">
              {files.map((f, i) => (
                <li key={i} className="flex items-center justify-between gap-2">
                  <span className="truncate">{f.name}</span>
                  <Button type="button" variant="ghost" size="sm" onClick={() => removeFile(i)}>Remove</Button>
                </li>
              ))}
            </ul>
          )}
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
