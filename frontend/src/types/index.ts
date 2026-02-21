export interface Category {
  id: number;
  name: string;
  slug: string;
  path: string;
  icon_url?: string;
  children?: Category[];
  items?: CategoryItem[];
}

export interface CategoryItem {
  id: number;
  name: string;
  sort_order: number;
  category?: number;
}

export interface ListingImage {
  id: string;
  url_thumb: string;
  url_medium: string;
  url_large: string;
  sort_order: number;
}

export interface Listing {
  id: string;
  title: string;
  description: string;
  seller_id: string;
  category_id: number;
  condition: "NEW" | "LIKE_NEW" | "GOOD" | "FAIR" | "POOR";
  listing_type: "AUCTION" | "BUY_IT_NOW" | "BOTH";
  buy_it_now_price?: number;
  starting_price?: number;
  reserve_price?: number;
  current_price: number;
  quantity: number;
  quantity_sold: number;
  start_time?: string;
  end_time?: string;
  auction_end_time?: string;
  status: "DRAFT" | "ACTIVE" | "ENDED" | "SOLD" | "CANCELLED";
  images: ListingImage[];
  view_count: number;
  watch_count: number;
  bid_count?: number;
  created_at: string;
  shipping_cost: number;
  shipping_from_country: string;
}

export interface LedgerEntry {
  id: string;
  entry_type: string;
  debit: string;
  credit: string;
  balance_after: string;
  reference_type: string;
  reference_id: string;
  created_at: string;
  description?: string;
}

export interface Order {
  id: string;
  listing_id: string;
  buyer_id: string;
  seller_id: string;
  amount: string;
  status: string;
  created_at: string;
}
