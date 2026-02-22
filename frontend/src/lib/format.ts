/**
 * Format a DOGE amount as whole number with USD equivalent in parentheses.
 */
export function formatDogeWithUsd(doge: number, rate: number): string {
  const dogeInt = Math.round(Number(doge));
  const usd = dogeInt * rate;
  const usdStr = usd.toFixed(2);
  return `${dogeInt.toLocaleString()} ($${usdStr})`;
}

/** Format DOGE only as whole number (no decimals). */
export function formatDoge(doge: number): string {
  return Math.round(Number(doge)).toLocaleString();
}
