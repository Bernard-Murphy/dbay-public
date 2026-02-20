export interface Category {
  id: number;
  name: string;
  slug: string;
  path: string;
  icon_url?: string;
  children?: Category[];
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
  status: "DRAFT" | "ACTIVE" | "ENDED" | "SOLD" | "CANCELLED";
  images: ListingImage[];
  view_count: number;
  watch_count: number;
  created_at: string;
  shipping_cost: number;
  shipping_from_country: string;
}
