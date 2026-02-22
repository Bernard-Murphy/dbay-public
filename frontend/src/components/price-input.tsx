import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DogeIcon } from "@/components/doge-icon";
import { useDogeRateStore } from "@/stores/doge-rate-store";

interface PriceInputProps {
  value: number;
  onChange: (doge: number) => void;
  label?: string;
  id?: string;
  min?: number;
}

/** Dual DOGE + USD price input. Value is always stored in whole DOGE. */
export function PriceInput({ value, onChange, label = "Amount", id = "price", min = 0 }: PriceInputProps) {
  const dogeRate = useDogeRateStore((s) => s.rate);
  const dogeInt = Math.round(Number(value));
  const usdValue = dogeInt * dogeRate;

  const handleDogeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = parseInt(e.target.value, 10);
    if (!Number.isNaN(v) && v >= min) {
      onChange(v);
    } else if (e.target.value === "" || e.target.value === "-") {
      onChange(min);
    }
  };

  const handleUsdChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const usd = parseFloat(e.target.value);
    if (!Number.isNaN(usd) && usd >= 0) {
      const doge = usd / dogeRate;
      onChange(Math.round(doge));
    } else if (e.target.value === "" || e.target.value === "-") {
      onChange(min);
    }
  };

  return (
    <div className="space-y-2">
      {label && (
        <Label htmlFor={id} className="flex items-center gap-1">
          <DogeIcon size={14} />
          {label}
        </Label>
      )}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label htmlFor={`${id}-doge`} className="text-xs text-muted-foreground block mb-1">
            DOGE
          </label>
          <Input
            id={`${id}-doge`}
            type="number"
            min={min}
            step={1}
            value={dogeInt}
            onChange={handleDogeChange}
          />
        </div>
        <div>
          <label htmlFor={`${id}-usd`} className="text-xs text-muted-foreground block mb-1">
            USD
          </label>
          <Input
            id={`${id}-usd`}
            type="number"
            min={0}
            step={0.01}
            value={usdValue.toFixed(2)}
            onChange={handleUsdChange}
          />
        </div>
      </div>
    </div>
  );
}
