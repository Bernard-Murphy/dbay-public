import { useSearchParams, Link } from "react-router-dom";
import { useListingStore } from "@/stores/listing-store";
import { useEffect } from "react";
import { format } from "date-fns";
import { Clock, Gavel, ShoppingCart, ChevronLeft, ChevronRight } from "lucide-react";
import { DogeIcon } from "@/components/doge-icon";
import { formatDogeWithUsd } from "@/lib/format";
import { useDogeRateStore } from "@/stores/doge-rate-store";
import { motion, AnimatePresence } from "framer-motion";
import { normalize, fade_out_scale_1, transition_fast } from "@/lib/transitions";
import Spinner from "@/components/ui/spinner";
import { SearchBar } from "@/components/search-bar";
import { useQuery } from "@/hooks/use-query";
import type { Category } from "@/types";
import { Button } from "@/components/ui/button";

const PLACEHOLDER_IMG = "https://via.placeholder.com/80?text=No+Image";
const PER_PAGE = 20;

export function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { listings, loading, searchTotal, searchListings } = useListingStore();
  const q = searchParams.get("q") ?? "";
  const category = searchParams.get("category") ?? "";
  const listingType = searchParams.get("listing_type") ?? "";
  const page = Math.max(1, parseInt(searchParams.get("page") ?? "1", 10));

  const dogeRate = useDogeRateStore((s) => s.rate);
  const { data: categoriesData } = useQuery<{ results?: Category[] }>(
    "categories/with-items/",
    { fallback: [] }
  );
  const categories = (Array.isArray(categoriesData) ? categoriesData : categoriesData?.results ?? []) as (Category & { items?: { id: number; name: string }[] })[];

  useEffect(() => {
    searchListings({ q, category, listing_type: listingType, page: String(page) });
  }, [q, category, listingType, page, searchListings]);

  const handleSearch = (params: {
    q: string;
    category: string;
    listing_type: string;
    date_from: string;
    date_to: string;
  }) => {
    const next = new URLSearchParams(searchParams);
    if (params.q) next.set("q", params.q);
    else next.delete("q");
    if (params.category) next.set("category", params.category);
    else next.delete("category");
    if (params.listing_type) next.set("listing_type", params.listing_type);
    else next.delete("listing_type");
    if (params.date_from) next.set("date_from", params.date_from);
    else next.delete("date_from");
    if (params.date_to) next.set("date_to", params.date_to);
    next.set("page", "1");
    setSearchParams(next);
  };

  const totalPages = Math.ceil(searchTotal / PER_PAGE) || 1;
  const setPage = (p: number) => {
    const next = new URLSearchParams(searchParams);
    next.set("page", String(Math.max(1, Math.min(p, totalPages))));
    setSearchParams(next);
  };

  const imageUrl = (listing: { images?: { url_thumb?: string; url_medium?: string }[] }) =>
    listing.images?.[0]?.url_thumb || listing.images?.[0]?.url_medium || PLACEHOLDER_IMG;

  const timeRemaining = (endTime?: string) => {
    if (!endTime) return null;
    const end = new Date(endTime).getTime();
    const now = Date.now();
    if (end <= now) return "Ended";
    const d = Math.floor((end - now) / 86400);
    const h = Math.floor(((end - now) % 86400) / 3600);
    return `${d}d ${h}h`;
  };

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      <div className="mb-6">
        <SearchBar
          key={`${q}-${category}-${listingType}`}
          initialQ={q}
          initialCategory={category}
          initialListingType={listingType}
          initialDateFrom={searchParams.get("date_from") ?? ""}
          initialDateTo={searchParams.get("date_to") ?? ""}
          categories={categories}
          onSearch={handleSearch}
          showAdvanced={true}
        />
      </div>
      <h1 className="text-2xl font-bold mb-2">Search Results</h1>
      <p className="text-muted-foreground mb-6">
        {loading ? "..." : `${searchTotal} result${searchTotal !== 1 ? "s" : ""}`}
      </p>
      <AnimatePresence mode="wait">
        {!loading && listings.length === 0 && (
          <motion.p initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="text-muted-foreground">No listings found.</motion.p>
        )}
        {!loading && listings.length > 0 && (
          <motion.ul initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="space-y-0 divide-y border rounded-lg overflow-hidden">
            {listings.map((listing) => (
              <li key={listing.id}>
                <Link
                  to={`/listings/${listing.id}`}
                  className="flex gap-4 p-4 hover:bg-muted/50 transition-colors"
                >
                  <img
                    src={imageUrl(listing)}
                    alt=""
                    className="w-20 h-20 object-cover rounded flex-shrink-0 bg-muted"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{listing.title}</p>
                    <p className="text-primary font-semibold flex items-center gap-1">
                      <DogeIcon size={18} />
                      {formatDogeWithUsd(Number(listing.current_price), dogeRate)}
                    </p>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground mt-1">
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {listing.created_at ? format(new Date(listing.created_at), "MMM d, yyyy") : "—"}
                      </span>
                      {listing.listing_type === "AUCTION" && (
                        <>
                          <span className="flex items-center gap-1">
                            <Gavel className="h-3 w-3" />
                            Auction
                          </span>
                          <span>{timeRemaining(listing.auction_end_time || listing.end_time)} left</span>
                          {listing.bid_count != null && <span>{listing.bid_count} bids</span>}
                        </>
                      )}
                      {listing.listing_type === "BUY_IT_NOW" && (
                        <span className="flex items-center gap-1">
                          <ShoppingCart className="h-3 w-3" />
                          Buy It Now
                        </span>
                      )}
                    </div>
                  </div>
                </Link>
              </li>
            ))}
          </motion.ul>
        )}
        {loading && <motion.div key="loading" initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="p-4 flex items-center justify-center"><Spinner size="sm" /></motion.div>}
      </AnimatePresence>
      {!loading && listings.length > 0 && searchTotal > PER_PAGE && (
        <nav className="mt-6 flex items-center justify-center gap-2" aria-label="Pagination">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(page - 1)}
            disabled={page <= 1}
          >
            <ChevronLeft className="h-4 w-4" />
            Previous
          </Button>
          <span className="text-sm text-muted-foreground px-2">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage(page + 1)}
            disabled={page >= totalPages}
          >
            Next
            <ChevronRight className="h-4 w-4" />
          </Button>
        </nav>
      )}
    </div>
  );
}
