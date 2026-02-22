import { useEffect, useState } from "react";
import { api } from "@/services/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CategoryIcon } from "@/components/category-icon";
import { ChevronDown, Plus, Trash2 } from "lucide-react";

interface Dispute {
  id: string;
  reason: string;
  status: string;
}

interface CategoryItem {
  id: number;
  name: string;
  sort_order: number;
  image_url?: string | null;
}

interface CategoryWithItems {
  id: number;
  name: string;
  slug: string;
  default_icon?: string;
  icon_url?: string | null;
  sort_order: number;
  items: CategoryItem[];
}

const ICON_OPTIONS = ["car", "shirt", "smartphone", "home", "circle-dot", "gamepad-2", "book-open", "star", "gem"];

export function AdminDashboardPage() {
  const [disputes, setDisputes] = useState<Dispute[]>([]);
  const [categories, setCategories] = useState<CategoryWithItems[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [newItemName, setNewItemName] = useState<Record<number, string>>({});
  const [newItemImage, setNewItemImage] = useState<Record<number, string>>({});
  const [editCategory, setEditCategory] = useState<Record<number, { name: string; default_icon: string }>>({});

  useEffect(() => {
    api.get("/order/disputes/").then((res) => setDisputes(Array.isArray(res.data) ? res.data : [])).catch(() => setDisputes([]));
  }, []);

  useEffect(() => {
    api.get("/categories/with-items/").then((res) => setCategories(Array.isArray(res.data) ? res.data : [])).catch(() => setCategories([]));
  }, []);

  const refreshCategories = () => {
    api.get("/categories/with-items/").then((res) => setCategories(Array.isArray(res.data) ? res.data : [])).catch(() => { });
  };

  const handleAddItem = async (categoryId: number) => {
    const name = newItemName[categoryId]?.trim();
    if (!name) return;
    try {
      await api.post(`/categories/${categoryId}/items/`, { name, image_url: newItemImage[categoryId] || null });
      setNewItemName((p) => ({ ...p, [categoryId]: "" }));
      setNewItemImage((p) => ({ ...p, [categoryId]: "" }));
      refreshCategories();
    } catch (e) {
      console.error(e);
    }
  };

  const handleDeleteItem = async (categoryId: number, itemId: number) => {
    try {
      await api.delete(`/categories/${categoryId}/items/${itemId}/`);
      refreshCategories();
    } catch (e) {
      console.error(e);
    }
  };

  const handlePatchCategory = async (categoryId: number) => {
    const edit = editCategory[categoryId];
    if (!edit) return;
    try {
      await api.patch(`/categories/${categoryId}/`, { name: edit.name, default_icon: edit.default_icon || "" });
      setEditCategory((p) => ({ ...p, [categoryId]: undefined! }));
      refreshCategories();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="container max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="rounded-lg border bg-card p-6">
          <dt className="text-sm text-muted-foreground">Total Disputes</dt>
          <dd className="text-3xl font-semibold mt-1">{disputes.length}</dd>
        </div>
      </div>
      <div className="rounded-lg border overflow-hidden mb-8">
        <h2 className="font-semibold p-4 border-b">Recent Disputes</h2>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b bg-muted/50">
              <th className="text-left p-3">ID</th>
              <th className="text-left p-3">Reason</th>
              <th className="text-left p-3">Status</th>
              <th className="text-right p-3">Action</th>
            </tr>
          </thead>
          <tbody>
            {disputes.map((d) => (
              <tr key={d.id} className="border-b">
                <td className="p-3">{d.id}</td>
                <td className="p-3">{d.reason}</td>
                <td className="p-3">{d.status}</td>
                <td className="p-3 text-right"><a href="#" className="text-primary hover:underline">View</a></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="font-semibold text-xl mb-4">Categories & Items</h2>
      <div className="space-y-2">
        {categories.map((cat) => (
          <div key={cat.id} className="rounded-lg border bg-card overflow-hidden">
            <button
              type="button"
              className="w-full flex items-center gap-2 p-4 text-left hover:bg-muted/50"
              onClick={() => setExpandedId(expandedId === cat.id ? null : cat.id)}
            >
              <ChevronDown className={`h-4 w-4 transition-transform ${expandedId === cat.id ? "rotate-180" : ""}`} />
              <CategoryIcon defaultIcon={cat.default_icon} iconUrl={cat.icon_url} size={20} />
              <span className="font-medium">{cat.name}</span>
            </button>
            {expandedId === cat.id && (
              <div className="p-4 pt-0 border-t space-y-4">
                <div className="flex flex-wrap gap-4 items-end">
                  <div>
                    <Label className="text-xs">Category name</Label>
                    <Input
                      className="w-48"
                      value={editCategory[cat.id]?.name ?? cat.name}
                      onChange={(e) =>
                        setEditCategory((p) => ({
                          ...p,
                          [cat.id]: { ...(p[cat.id] ?? { name: cat.name, default_icon: cat.default_icon ?? "" }), name: e.target.value },
                        }))
                      }
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Icon</Label>
                    <select
                      className="rounded-md border bg-background px-3 py-2 text-sm w-36"
                      value={editCategory[cat.id]?.default_icon ?? cat.default_icon ?? ""}
                      onChange={(e) =>
                        setEditCategory((p) => ({
                          ...p,
                          [cat.id]: { ...(p[cat.id] ?? { name: cat.name, default_icon: cat.default_icon ?? "" }), default_icon: e.target.value },
                        }))
                      }
                    >
                      {ICON_OPTIONS.map((opt) => (
                        <option key={opt} value={opt}>{opt}</option>
                      ))}
                    </select>
                  </div>
                  <Button size="sm" onClick={() => handlePatchCategory(cat.id)}>Save category</Button>
                </div>
                <div>
                  <Label className="text-sm font-medium">Items</Label>
                  <ul className="mt-2 space-y-1">
                    {cat.items.map((item) => (
                      <li key={item.id} className="flex items-center gap-2 text-sm">
                        <span>{item.name}</span>
                        {item.image_url && <span className="text-muted-foreground truncate max-w-[200px]">({item.image_url})</span>}
                        <Button type="button" variant="ghost" size="sm" className="text-destructive h-7 w-7 p-0" onClick={() => handleDeleteItem(cat.id, item.id)}>
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="flex gap-2 items-end">
                  <div>
                    <Label className="text-xs">New item name</Label>
                    <Input
                      placeholder="Item name"
                      value={newItemName[cat.id] ?? ""}
                      onChange={(e) => setNewItemName((p) => ({ ...p, [cat.id]: e.target.value }))}
                    />
                  </div>
                  <div>
                    <Label className="text-xs">Default image URL</Label>
                    <Input
                      placeholder="https://..."
                      value={newItemImage[cat.id] ?? ""}
                      onChange={(e) => setNewItemImage((p) => ({ ...p, [cat.id]: e.target.value }))}
                    />
                  </div>
                  <Button size="sm" onClick={() => handleAddItem(cat.id)}><Plus className="h-4 w-4 mr-1" /> Add item</Button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
