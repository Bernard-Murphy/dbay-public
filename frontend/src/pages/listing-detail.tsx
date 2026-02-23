import { useParams, Link } from "react-router-dom";
import { useEffect, useState, useCallback } from "react";
import { useListingStore } from "@/stores/listing-store";
import { BidPanel } from "@/components/listings/bid-panel";
import { Button } from "@/components/ui/button";
import { DogeIcon } from "@/components/doge-icon";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Textarea } from "@/components/ui/textarea";
import { formatDogeWithUsd, formatDoge } from "@/lib/format";
import { useDogeRateStore } from "@/stores/doge-rate-store";
import { motion } from "framer-motion";
import { normalize, fade_out_scale_1, transition_fast } from "@/lib/transitions";
import { api } from "@/services/api";
import { format } from "date-fns";

const PLACEHOLDER_IMG = "https://feednana.com/random";

interface ListingAnswer {
  id: string;
  body: string;
  author_id: string;
  created_at: string;
}

interface ListingQuestion {
  id: string;
  body: string;
  author_id: string;
  created_at: string;
  answers: ListingAnswer[];
}

interface Bid {
  id: number;
  amount: string;
  bidder_id: string;
  created_at: string;
}

export function ListingDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { currentListing, loading, error, fetchListing } = useListingStore();
  const dogeRate = useDogeRateStore((s) => s.rate);
  const [currentMedia, setCurrentMedia] = useState<{ url: string; type: "image" | "video" }>({ url: id ? `${PLACEHOLDER_IMG}?id=${id}` : PLACEHOLDER_IMG, type: "image" });
  const [questions, setQuestions] = useState<ListingQuestion[]>([]);
  const [bids, setBids] = useState<Bid[]>([]);
  const [questionBody, setQuestionBody] = useState("");
  const [answerBodies, setAnswerBodies] = useState<Record<string, string>>({});
  const [submittingQuestion, setSubmittingQuestion] = useState(false);
  const [submittingAnswer, setSubmittingAnswer] = useState<string | null>(null);
  const [seller, setSeller] = useState<{ id: string; username: string; display_name?: string; avatar_url?: string | null } | null>(null);

  useEffect(() => {
    if (id) fetchListing(id);
  }, [id, fetchListing]);

  useEffect(() => {
    if (!id) return;
    api.get(`/questions/listings/${id}/questions/`).then((r) => setQuestions(Array.isArray(r.data) ? r.data : [])).catch(() => setQuestions([]));
  }, [id]);

  const fetchBids = useCallback(() => {
    if (!id) return;
    api.get(`/auction/auctions/${id}/bids/`).then((r) => setBids(Array.isArray(r.data) ? r.data : [])).catch(() => setBids([]));
  }, [id]);

  const handleBidSuccess = useCallback(() => {
    fetchBids();
    if (id) fetchListing(id);
  }, [fetchBids, fetchListing, id]);

  useEffect(() => {
    if (!id || currentListing?.listing_type !== "AUCTION") return;
    fetchBids();
  }, [id, currentListing?.listing_type, fetchBids]);

  useEffect(() => {
    if (!currentListing?.seller_id) return;
    api.get(`/user/users/${currentListing.seller_id}/`).then((r) => setSeller(r.data)).catch(() => setSeller(null));
  }, [currentListing?.seller_id]);

  useEffect(() => {
    const placeholderUrl = id ? `${PLACEHOLDER_IMG}?id=${id}` : PLACEHOLDER_IMG;
    if (currentListing?.images?.length) {
      const first = currentListing.images[0];
      const url = first.url_large || first.url_medium || first.url_thumb || placeholderUrl;
      const type = (first as { media_type?: string }).media_type === "video" ? "video" : "image";
      setCurrentMedia({ url, type });
    } else if (currentListing) {
      setCurrentMedia({ url: placeholderUrl, type: "image" });
    }
  }, [currentListing, id]);

  if (loading) return <div className="container py-20 text-center"></div>;
  if (error) return <div className="container py-20 text-center text-destructive">{error}</div>;
  if (!currentListing) return <div className="container py-20 text-center">Listing not found.</div>;

  const listing = currentListing;

  return (
    <motion.div initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="container max-w-6xl mx-auto px-4 py-8">
      <div className="grid lg:grid-cols-2 gap-8">
        <div>
          <div className="aspect-square rounded-lg overflow-hidden bg-muted mb-4">
            {currentMedia.type === "video" ? (
              <video src={currentMedia.url} controls className="w-full h-full object-cover" />
            ) : (
              <img src={currentMedia.url} alt={listing.title} className="w-full h-full object-cover" />
            )}
          </div>
          {listing.images && listing.images.length > 1 && (
            <div className="flex gap-2 overflow-x-auto">
              {listing.images.map((img, idx) => {
                const url = img.url_large || img.url_medium || img.url_thumb || `${PLACEHOLDER_IMG}?id=${id}-${img.id ?? idx}`;
                const isVideo = (img as { media_type?: string }).media_type === "video";
                return (
                  <button
                    key={img.id}
                    type="button"
                    onClick={() => setCurrentMedia({ url, type: isVideo ? "video" : "image" })}
                    className="w-16 h-16 flex-shrink-0 rounded overflow-hidden border-2 border-transparent focus:border-primary"
                  >
                    {isVideo ? (
                      <video src={url} className="w-full h-full object-cover" muted playsInline />
                    ) : (
                      <img src={url} alt="" className="w-full h-full object-cover" />
                    )}
                  </button>
                );
              })}
            </div>
          )}
        </div>
        <div>
          <h1 className="text-3xl font-bold">{listing.title}</h1>
          <p className="text-2xl text-primary mt-2 flex items-center gap-2">
            <DogeIcon size={28} />
            {formatDogeWithUsd(Number(listing.current_price), dogeRate)}
          </p>
          <div className="mt-6 prose dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: listing.description }} />
          {seller && (
            <div className="mt-6 p-4 rounded-lg border bg-muted/30">
              <p className="text-sm text-muted-foreground mb-2">Seller</p>
              <Link to={`/users/${seller.id}`} className="flex items-center gap-3 hover:opacity-80 transition-opacity">
                <Avatar className="h-10 w-10">
                  <AvatarImage src={seller.avatar_url ?? undefined} alt="" />
                  <AvatarFallback>{(seller.display_name || seller.username || "?")[0]}</AvatarFallback>
                </Avatar>
                <span className="font-medium">{seller.display_name || seller.username}</span>
                <span className="text-muted-foreground text-sm">@{seller.username}</span>
              </Link>
            </div>
          )}
          <dl className="mt-6 grid grid-cols-2 gap-2 text-sm">
            <dt className="text-muted-foreground">Condition</dt>
            <dd>{listing.condition}</dd>
            <dt className="text-muted-foreground">Category</dt>
            <dd>{listing.category_id}</dd>
            <dt className="text-muted-foreground">Type</dt>
            <dd>{listing.listing_type}</dd>
          </dl>
          <div className="mt-8">
            {listing.listing_type === "AUCTION" && <BidPanel listing={listing} onBidSuccess={handleBidSuccess} />}
            {listing.listing_type !== "AUCTION" && (
              <Button asChild><Link to={`/listings/${listing.id}/buy`}>Buy Now</Link></Button>
            )}
          </div>
        </div>
      </div>

      <section className="mt-12 border-t pt-8">
        <h2 className="text-xl font-semibold mb-4">Questions &amp; Answers</h2>
        <div className="space-y-4">
          <div>
            <Textarea
              placeholder="Ask a question about this listing..."
              value={questionBody}
              onChange={(e) => setQuestionBody(e.target.value)}
              className="min-h-[80px]"
            />
            <Button
              type="button"
              size="sm"
              className="mt-2"
              disabled={!questionBody.trim() || submittingQuestion}
              onClick={async () => {
                if (!questionBody.trim() || !id) return;
                setSubmittingQuestion(true);
                try {
                  await api.post(`/questions/listings/${id}/questions/`, { body: questionBody.trim() });
                  setQuestionBody("");
                  const r = await api.get(`/questions/listings/${id}/questions/`);
                  setQuestions(Array.isArray(r.data) ? r.data : []);
                } finally {
                  setSubmittingQuestion(false);
                }
              }}
            >
              {submittingQuestion ? "Posting..." : "Ask question"}
            </Button>
          </div>
          <ul className="space-y-4">
            {questions.map((q) => (
              <li key={q.id} className="rounded-lg border p-4">
                <p className="font-medium text-sm text-muted-foreground">Question · {format(new Date(q.created_at), "MMM d, yyyy")}</p>
                <p className="mt-1">{q.body}</p>
                {q.answers?.length > 0 && (
                  <ul className="mt-3 ml-4 space-y-2 border-l-2 pl-4">
                    {q.answers.map((a) => (
                      <li key={a.id}>
                        <p className="text-sm text-muted-foreground">Answer · {format(new Date(a.created_at), "MMM d, yyyy")}</p>
                        <p className="mt-0.5">{a.body}</p>
                      </li>
                    ))}
                  </ul>
                )}
                <div className="mt-2">
                  <Textarea
                    placeholder="Answer this question..."
                    value={answerBodies[q.id] ?? ""}
                    onChange={(e) => setAnswerBodies((p) => ({ ...p, [q.id]: e.target.value }))}
                    className="min-h-[60px] text-sm"
                  />
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    className="mt-1"
                    disabled={!answerBodies[q.id]?.trim() || submittingAnswer === q.id}
                    onClick={async () => {
                      const body = answerBodies[q.id]?.trim();
                      if (!body) return;
                      setSubmittingAnswer(q.id);
                      try {
                        await api.post(`/questions/questions/${q.id}/answers/`, { body });
                        setAnswerBodies((p) => ({ ...p, [q.id]: "" }));
                        const r = await api.get(`/questions/listings/${id}/questions/`);
                        setQuestions(Array.isArray(r.data) ? r.data : []);
                      } finally {
                        setSubmittingAnswer(null);
                      }
                    }}
                  >
                    {submittingAnswer === q.id ? "Posting..." : "Post answer"}
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </section>

      {listing.listing_type === "AUCTION" && bids.length > 0 && (
        <section className="mt-12 border-t pt-8">
          <h2 className="text-xl font-semibold mb-4">Bid history</h2>
          <ul className="space-y-2">
            {bids.map((b) => (
              <li key={b.id} className="flex items-center justify-between rounded-md border px-3 py-2 text-sm">
                <span className="flex items-center gap-2">
                  <DogeIcon size={16} />
                  {formatDoge(Number(b.amount))} DOGE
                </span>
                <span className="text-muted-foreground">{format(new Date(b.created_at), "MMM d, yyyy HH:mm")}</span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </motion.div>
  );
}
