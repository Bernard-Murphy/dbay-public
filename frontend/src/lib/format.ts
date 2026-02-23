/**
 * Format USD with thousands separators (e.g. $63,545.34).
 */
export function formatUsd(usd: number): string {
  return (
    "$" +
    Number(usd).toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
}

/**
 * Format a DOGE amount as whole number with USD equivalent in parentheses.
 */
export function formatDogeWithUsd(doge: number, rate: number): string {
  const dogeInt = Math.round(Number(doge));
  const usd = dogeInt * rate;
  return `${dogeInt.toLocaleString()} (${formatUsd(usd)})`;
}

/** Format DOGE only as whole number (no decimals). */
export function formatDoge(doge: number): string {
  return Math.round(Number(doge)).toLocaleString();
}
