import { useParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import { useListingStore } from "@/stores/listing-store";
import { BidPanel } from "@/components/listings/bid-panel";
import { Button } from "@/components/ui/button";

const PLACEHOLDER_IMG = "https://via.placeholder.com/600?text=No+Image";

export function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { currentListing, loading, error, fetchListing } = useListingStore();
  const [currentImage, setCurrentImage] = useState("");

  useEffect(() => {
    if (id) fetchListing(id);
  }, [id, fetchListing]);

  useEffect(() => {
    if (currentListing?.images?.length) {
      const img = currentListing.images[0];
      setCurrentImage(img.url_large || img.url_medium || PLACEHOLDER_IMG);
    } else if (currentListing) {
      setCurrentImage(PLACEHOLDER_IMG);
    }
  }, [currentListing]);

  if (loading) return <div className="container py-20 text-center">Loading...</div>;
  if (error) return <div className="container py-20 text-center text-destructive">{error}</div>;
  if (!currentListing) return <div className="container py-20 text-center">Listing not found.</div>;

  const listing = currentListing;

  return (
    <div className="container max-w-6xl mx-auto px-4 py-8">
      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <div className="aspect-square rounded-lg overflow-hidden bg-muted mb-4">
            <img src={currentImage} alt={listing.title} className="w-full h-full object-cover" />
          </div>
          {listing.images && listing.images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto">
              {listing.images.map((img) => (
                <button
                  key={img.id}
                  type="button"
                  onClick={() => setCurrentImage(img.url_large || img.url_medium || PLACEHOLDER_IMG)}
                  className="w-16 h-16 flex-shrink-0 rounded overflow-hidden border-2 border-transparent focus:border-primary"
                >
                  <img src={img.url_thumb || img.url_medium} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}
        </div>
        <div>
          <h1 className="text-3xl font-bold">{listing.title}</h1>
          <p className="text-2xl text-primary mt-2">Ð{listing.current_price}</p>
          <div className="mt-6 prose dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: listing.description }} />
          <dl className="mt-6 grid grid-cols-2 gap-2 text-sm">
            <dt className="text-muted-foreground">Condition</dt>
            <dd>{listing.condition}</dd>
            <dt className="text-muted-foreground">Category</dt>
            <dd>{listing.category_id}</dd>
            <dt className="text-muted-foreground">Type</dt>
            <dd>{listing.listing_type}</dd>
          </dl>
          <div className="mt-8">
            {listing.listing_type === "AUCTION" && <BidPanel listing={listing} />}
            {listing.listing_type !== "AUCTION" && (
              <Button asChild><Link to={`/listings/${listing.id}/buy`}>Buy Now</Link></Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
