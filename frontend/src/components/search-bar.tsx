import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ChevronDown } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";
import { retract, normalize, transition_fast } from "@/lib/transitions";
import type { Category } from "@/types";

export interface SearchBarParams {
  q: string;
  category: string;
  listing_type: string;
  date_from: string;
  date_to: string;
}

interface SearchBarProps {
  initialQ?: string;
  initialCategory?: string;
  initialListingType?: string;
  initialDateFrom?: string;
  initialDateTo?: string;
  categories?: (Category & { items?: { id: number; name: string }[] })[];
  onSearch: (params: SearchBarParams) => void;
  showAdvanced?: boolean;
}

export function SearchBar({
  initialQ = "",
  initialCategory = "",
  initialListingType = "",
  initialDateFrom = "",
  initialDateTo = "",
  categories = [],
  onSearch,
  showAdvanced = true,
}: SearchBarProps) {
  const [q, setQ] = useState(initialQ);
  const [categoryId, setCategoryId] = useState(initialCategory);
  const [listingType, setListingType] = useState(initialListingType);
  const [dateFrom, setDateFrom] = useState(initialDateFrom);
  const [dateTo, setDateTo] = useState(initialDateTo);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const handleSubmit = () => {
    onSearch({
      q,
      category: categoryId,
      listing_type: listingType,
      date_from: dateFrom,
      date_to: dateTo,
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          placeholder="Search listings..."
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          className="max-w-md"
        />
        <Button onClick={handleSubmit}>Search</Button>
      </div>
      {showAdvanced && (
        <>
          <div style={{ width: "max-content" }} className="mb-2">
            <Button
              onClick={() => setAdvancedOpen(!advancedOpen)}
              variant="ghost"
              size="sm"
              className="gap-2"
            >
              <ChevronDown
                className={`h-4 w-4 transition-transform ${advancedOpen ? "rotate-180" : ""}`}
              />
              Advanced filters
            </Button>
          </div>
          <AnimatePresence mode="wait">
            {advancedOpen && (
              <motion.div
                initial={retract}
                animate={{ ...normalize, height: "auto" }}
                exit={retract}
                transition={transition_fast}
                key={advancedOpen ? "open" : "closed"}
                className="overflow-hidden"
              >
                <div className="flex flex-wrap gap-4 p-4 rounded-lg border bg-card">
                  <div>
                    <label className="text-sm text-muted-foreground mr-2">Category</label>
                    <select
                      value={categoryId}
                      onChange={(e) => setCategoryId(e.target.value)}
                      className="rounded-md border bg-background px-3 py-2 text-sm"
                    >
                      <option value="">Any</option>
                      {Array.isArray(categories) &&
                        categories.map((c) => (
                          <option key={c.id} value={String(c.id)}>
                            {c.name}
                          </option>
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
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}
    </div>
  );
}
