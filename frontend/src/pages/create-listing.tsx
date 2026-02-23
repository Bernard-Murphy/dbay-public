import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PriceInput } from "@/components/price-input";
import { FilePreview } from "@/components/file-preview";
import { useQuery } from "@/hooks/use-query";
import { useListingStore } from "@/stores/listing-store";
import type { Listing } from "@/types";
import { toast } from "sonner";

const CONDITIONS = ["NEW", "LIKE_NEW", "GOOD", "FAIR", "POOR"] as const;
const TYPES = ["AUCTION", "BUY_IT_NOW", "BOTH"] as const;

export function CreateListingPage() {
  const navigate = useNavigate();
  const { createListing, error: storeError } = useListingStore();
  const { data: categoriesData } = useQuery<{ results?: { id: number; name: string }[] } | { id: number; name: string }[]>(
    "categories/with-items/",
    { fallback: [] }
  );
  const categories = (Array.isArray(categoriesData) ? categoriesData : categoriesData?.results ?? []) as { id: number; name: string }[];

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
    category_id: undefined,
  });
  const [files, setFiles] = useState<File[]>([]);
  const [fileError, setFileError] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [fileProgress, setFileProgress] = useState<Record<number, number>>({});

  const MAX_VIDEO_BYTES = 100 * 1024 * 1024; // 100MB

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const chosen = Array.from(e.target.files ?? []);
    const err = chosen.find((f) => f.type.startsWith("video/") && f.size > MAX_VIDEO_BYTES);
    if (err) {
      const msg = `Video "${err.name}" is over 100MB. Max size for videos is 100MB.`;
      setFileError(msg);
      toast.error(msg);
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
    setFileProgress({});
    setLoading(true);
    try {
      const created = await createListing(form, files, (index, percent) => {
        setFileProgress((prev) => ({ ...prev, [index]: percent }));
      });
      toast.success("Listing created.");
      navigate(`/listings/${created.id}`);
    } catch {
      toast.error("Failed to create listing.");
    } finally {
      setLoading(false);
      setFileProgress({});
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
          <Label htmlFor="category">Category</Label>
          <select
            id="category"
            value={form.category_id ?? ""}
            onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value ? Number(e.target.value) : undefined }))}
            className="w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
            required
          >
            <option value="">Select a category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.id}>{cat.name}</option>
            ))}
          </select>
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
          {files.length > 0 && (
            <ul className="mt-2 space-y-3">
              {files.map((f, i) => (
                <li key={i} className="flex items-center gap-3 p-2 rounded-lg border">
                  <FilePreview file={f} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{f.name}</p>
                    {loading && fileProgress[i] !== undefined && (
                      <div className="mt-1 h-1.5 w-full rounded-full bg-muted overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all duration-300"
                          style={{ width: `${fileProgress[i]}%` }}
                        />
                      </div>
                    )}
                  </div>
                  <Button type="button" variant="ghost" size="sm" onClick={() => removeFile(i)} disabled={loading}>
                    Remove
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="flex gap-2">
          <Button type="submit" disabled={loading}>{loading ? "Creating..." : "Create Listing"}</Button>
          <Button type="button" variant="outline" onClick={() => navigate(-1)}>Cancel</Button>
        </div>
      </form>
    </div>
  );
}
