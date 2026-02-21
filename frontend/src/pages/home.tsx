import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { ChevronDown } from "lucide-react";
import { api } from "@/services/api";
import { useQuery } from "@/hooks/use-query";
import type { Category } from "@/types";

export function HomePage() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [categoryId, setCategoryId] = useState<string>("");
  const [listingType, setListingType] = useState<string>("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");

  const { data: categoriesData } = useQuery<{ results?: Category[] }>(
    "categories/with-items/",
    { fallback: [] }
  );
  const categories = (Array.isArray(categoriesData) ? categoriesData : categoriesData?.results ?? []) as (Category & { items?: { id: number; name: string }[] })[];

  const handleSearch = () => {
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (categoryId) params.set("category", categoryId);
    if (listingType) params.set("listing_type", listingType);
    if (dateFrom) params.set("date_from", dateFrom);
    if (dateTo) params.set("date_to", dateTo);
    navigate(`/search?${params.toString()}`);
  };

  const handleCategoryItemClick = (categoryId: number, itemName: string) => {
    navigate(`/search?q=${encodeURIComponent(itemName)}&category=${categoryId}`);
  };

  return (
    <div className="container max-w-6xl mx-auto px-4 py-8">
      <div className="space-y-4">
        <div className="flex gap-2">
          <Input
            placeholder="Search listings..."
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
            className="max-w-md"
          />
          <Button onClick={handleSearch}>Search</Button>
        </div>
        <Collapsible open={advancedOpen} onOpenChange={setAdvancedOpen}>
          <CollapsibleTrigger asChild>
            <Button variant="ghost" size="sm" className="gap-2">
              <ChevronDown className={`h-4 w-4 transition-transform ${advancedOpen ? "rotate-180" : ""}`} />
              Advanced filters
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent>
            <div className="flex flex-wrap gap-4 mt-2 p-4 rounded-lg border bg-card">
              <div>
                <label className="text-sm text-muted-foreground mr-2">Category</label>
                <select
                  value={categoryId}
                  onChange={(e) => setCategoryId(e.target.value)}
                  className="rounded-md border bg-background px-3 py-2 text-sm"
                >
                  <option value="">Any</option>
                  {Array.isArray(categories) && categories.map((c) => (
                    <option key={c.id} value={String(c.id)}>{c.name}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-sm text-muted-foreground mr-2">Type</label>
                <select
                  value={listingType}
                  onChange={(e) => setListingType(e.target.value)}
                  className="rounded-md border bg-background px-3 py-2 text-sm"
                >
                  <option value="">All</option>
                  <option value="AUCTION">Auction</option>
                  <option value="BUY_IT_NOW">Buy It Now</option>
                </select>
              </div>
              <div>
                <label className="text-sm text-muted-foreground mr-2">From</label>
                <input
                  type="date"
                  value={dateFrom}
                  onChange={(e) => setDateFrom(e.target.value)}
                  className="rounded-md border bg-background px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground mr-2">To</label>
                <input
                  type="date"
                  value={dateTo}
                  onChange={(e) => setDateTo(e.target.value)}
                  className="rounded-md border bg-background px-3 py-2 text-sm"
                />
              </div>
            </div>
          </CollapsibleContent>
        </Collapsible>
      </div>

      <section className="mt-12">
        <h2 className="text-xl font-semibold mb-4">Browse by Category</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.isArray(categories) && categories.length > 0 ? (
            categories.map((cat) => (
              <div
                key={cat.id}
                className="rounded-lg border bg-card p-4"
              >
                <h3 className="font-medium mb-2">{cat.name}</h3>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {(cat.items || []).map((item: { id: number; name: string }) => (
                    <li key={item.id}>
                      <button
                        type="button"
                        className="hover:text-foreground hover:underline text-left"
                        onClick={() => handleCategoryItemClick(cat.id, item.name)}
                      >
                        {item.name}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))
          ) : (
            <div className="col-span-full rounded-lg border bg-card p-8 text-center text-muted-foreground">
              <p>No categories loaded. Categories will appear here once the API is available.</p>
              <p className="mt-2 text-sm">Try: Automobiles, Men&apos;s Apparel, Electronics, etc.</p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
