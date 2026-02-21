import { useEffect } from "react";
import { useWalletStore } from "@/stores/wallet-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { format } from "date-fns";

export function WalletPage() {
  const { balance, depositAddress, history, loading, fetchBalance, fetchDepositAddress, fetchHistory, withdraw } = useWalletStore();
  const [amount, setAmount] = useState("");
  const [address, setAddress] = useState("");
  const [withdrawLoading, setWithdrawLoading] = useState(false);
  const [withdrawError, setWithdrawError] = useState("");

  useEffect(() => {
    fetchBalance();
    fetchDepositAddress();
    fetchHistory();
  }, [fetchBalance, fetchDepositAddress, fetchHistory]);

  const handleWithdraw = async (e: React.FormEvent) => {
    e.preventDefault();
    setWithdrawError("");
    setWithdrawLoading(true);
    try {
      await withdraw(parseFloat(amount), address);
      setAmount("");
      setAddress("");
    } catch (e) {
      setWithdrawError((e as Error).message);
    } finally {
      setWithdrawLoading(false);
    }
  };

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Wallet</h1>
      <div className="rounded-lg border bg-card p-6 mb-8">
        <h2 className="font-semibold mb-4">Your Balance</h2>
        <dl className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <dt className="text-sm text-muted-foreground">Available</dt>
            <dd className="text-2xl font-bold text-primary">Ð{balance?.available ?? 0}</dd>
          </div>
          <div>
            <dt className="text-sm text-muted-foreground">Locked</dt>
            <dd>Ð{balance?.locked ?? 0}</dd>
          </div>
          <div>
            <dt className="text-sm text-muted-foreground">Pending</dt>
            <dd>Ð{balance?.pending ?? 0}</dd>
          </div>
        </dl>
      </div>
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-semibold mb-2">Deposit Dogecoin</h2>
          <p className="text-sm text-muted-foreground mb-2">Send DOGE to this address.</p>
          <p className="break-all font-mono text-sm bg-muted p-3 rounded">{depositAddress || "Loading..."}</p>
          {depositAddress && (
            <img
              src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(depositAddress)}`}
              alt="Deposit QR"
              className="mt-4"
            />
          )}
        </div>
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-semibold mb-4">Withdraw</h2>
          <form onSubmit={handleWithdraw} className="space-y-4">
            <div>
              <Label htmlFor="withdraw-address">Destination Address</Label>
              <Input id="withdraw-address" value={address} onChange={(e) => setAddress(e.target.value)} required />
            </div>
            <div>
              <Label htmlFor="withdraw-amount">Amount (Ð)</Label>
              <Input
                id="withdraw-amount"
                type="number"
                min="0.00000001"
                step="0.00000001"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                required
              />
            </div>
            {withdrawError && <p className="text-sm text-destructive">{withdrawError}</p>}
            <Button type="submit" disabled={withdrawLoading}>{withdrawLoading ? "Processing..." : "Withdraw"}</Button>
          </form>
        </div>
      </div>
      <div className="rounded-lg border overflow-hidden">
        <h2 className="font-semibold p-4 border-b">Transaction History</h2>
        {loading && <p className="p-4 text-muted-foreground">Loading...</p>}
        {!loading && (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-left p-3">Date</th>
                <th className="text-left p-3">Type</th>
                <th className="text-left p-3">Description</th>
                <th className="text-right p-3">Amount</th>
              </tr>
            </thead>
            <tbody>
              {(history ?? []).map((entry) => (
                <tr key={entry.id} className="border-b">
                  <td className="p-3">{format(new Date(entry.created_at), "MMM d, yyyy HH:mm")}</td>
                  <td className="p-3">{entry.entry_type}</td>
                  <td className="p-3">{entry.description ?? entry.reference_type}</td>
                  <td className={`p-3 text-right ${Number(entry.credit) > 0 ? "text-green-600" : "text-red-600"}`}>
                    {Number(entry.credit) > 0 ? "+" : "-"}Ð{Number(entry.credit) > 0 ? entry.credit : entry.debit}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
