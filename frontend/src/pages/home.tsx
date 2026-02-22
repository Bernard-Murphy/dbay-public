import { useNavigate } from "react-router-dom";
import { useQuery } from "@/hooks/use-query";
import { CategoryIcon } from "@/components/category-icon";
import { SearchBar } from "@/components/search-bar";
import type { Category } from "@/types";

export function HomePage() {
  const navigate = useNavigate();

  const { data: categoriesData } = useQuery<{ results?: Category[] }>(
    "categories/with-items/",
    { fallback: [] }
  );
  const categories = (Array.isArray(categoriesData) ? categoriesData : categoriesData?.results ?? []) as (Category & { items?: { id: number; name: string }[] })[];

  const handleSearch = (params: {
    q: string;
    category: string;
    listing_type: string;
    date_from: string;
    date_to: string;
  }) => {
    const searchParams = new URLSearchParams();
    if (params.q) searchParams.set("q", params.q);
    if (params.category) searchParams.set("category", params.category);
    if (params.listing_type) searchParams.set("listing_type", params.listing_type);
    if (params.date_from) searchParams.set("date_from", params.date_from);
    if (params.date_to) searchParams.set("date_to", params.date_to);
    searchParams.set("page", "1");
    navigate(`/search?${searchParams.toString()}`);
  };

  const handleCategoryItemClick = (categoryId: number, itemName: string) => {
    navigate(`/search?q=${encodeURIComponent(itemName)}&category=${categoryId}&page=1`);
  };

  return (
    <div className="container max-w-6xl mx-auto px-4 py-8">
      <div className="space-y-4">
        <SearchBar
          categories={categories}
          onSearch={handleSearch}
          showAdvanced={true}
        />
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
                <div className="flex items-center gap-2 mb-2">
                  <CategoryIcon defaultIcon={cat.default_icon} iconUrl={cat.icon_url} size={22} />
                  <h3 className="font-medium">{cat.name}</h3>
                </div>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {(cat.items || [])
                    .filter((item: { id: number; name: string }) => item.name !== "Other")
                    .map((item: { id: number; name: string }) => (
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
