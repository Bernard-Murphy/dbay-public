import { useSearchParams, Link } from "react-router-dom";
import { useListingStore } from "@/stores/listing-store";
import { useEffect } from "react";
import { format } from "date-fns";
import { Clock, Gavel, ShoppingCart } from "lucide-react";

const PLACEHOLDER_IMG = "https://via.placeholder.com/80?text=No+Image";

export function SearchPage() {
  const [searchParams] = useSearchParams();
  const { listings, loading, fetchListings } = useListingStore();
  const q = searchParams.get("q") ?? "";
  const category = searchParams.get("category") ?? "";
  const listingType = searchParams.get("listing_type") ?? "";

  useEffect(() => {
    const params: Record<string, string> = {};
    if (q) params.q = q;
    if (category) params.category = category;
    if (listingType) params.listing_type = listingType;
    fetchListings(params);
  }, [q, category, listingType, fetchListings]);

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
      <h1 className="text-2xl font-bold mb-6">Search Results</h1>
      {loading && <p className="text-muted-foreground">Loading...</p>}
      {!loading && listings.length === 0 && (
        <p className="text-muted-foreground">No listings found.</p>
      )}
      {!loading && listings.length > 0 && (
        <ul className="space-y-0 divide-y border rounded-lg overflow-hidden">
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
                  <p className="text-primary font-semibold">Ð{listing.current_price}</p>
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
        </ul>
      )}
    </div>
  );
}
