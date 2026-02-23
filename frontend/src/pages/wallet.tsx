import { useEffect } from "react";
import { useWalletStore } from "@/stores/wallet-store";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { format } from "date-fns";
import { DogeIcon } from "@/components/doge-icon";
import { PriceInput } from "@/components/price-input";
import { formatDogeWithUsd } from "@/lib/format";
import { useDogeRateStore } from "@/stores/doge-rate-store";
import { motion, AnimatePresence } from "framer-motion";
import { normalize, fade_out_scale_1, transition_fast } from "@/lib/transitions";
import Spinner from "@/components/ui/spinner";

export function WalletPage() {
  const { balance, depositAddress, history, loading, fetchBalance, fetchDepositAddress, fetchHistory, withdraw, simulateDeposit } = useWalletStore();
  const dogeRate = useDogeRateStore((s) => s.rate);
  const [amount, setAmount] = useState(0);
  const [address, setAddress] = useState("");
  const [withdrawLoading, setWithdrawLoading] = useState(false);
  const [withdrawError, setWithdrawError] = useState("");
  const [simulateAmount, setSimulateAmount] = useState(100);
  const [simulateLoading, setSimulateLoading] = useState(false);
  const [simulateError, setSimulateError] = useState("");

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
      await withdraw(Math.floor(amount), address);
      setAmount(0);
      setAddress("");
    } catch (e) {
      setWithdrawError((e as Error).message);
    } finally {
      setWithdrawLoading(false);
    }
  };

  const handleSimulateDeposit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSimulateError("");
    setSimulateLoading(true);
    try {
      await simulateDeposit(simulateAmount);
    } catch (e) {
      setSimulateError((e as Error).message);
    } finally {
      setSimulateLoading(false);
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
            <dd className="text-2xl font-bold text-primary flex items-center gap-1">
              <DogeIcon size={24} />
              {formatDogeWithUsd(Number(balance?.available ?? 0), dogeRate)}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-muted-foreground">Locked</dt>
            <dd className="flex items-center gap-1">
              <DogeIcon size={16} />
              {formatDogeWithUsd(Number(balance?.locked ?? 0), dogeRate)}
            </dd>
          </div>
          <div>
            <dt className="text-sm text-muted-foreground">Pending</dt>
            <dd className="flex items-center gap-1">
              <DogeIcon size={16} />
              {formatDogeWithUsd(Number(balance?.pending ?? 0), dogeRate)}
            </dd>
          </div>
        </dl>
      </div>
      <div className="grid md:grid-cols-2 gap-8 mb-8">
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-semibold mb-2">Deposit Dogecoin</h2>
          <p className="text-sm text-muted-foreground mb-2">Send DOGE to this address.</p>
          <AnimatePresence mode="wait">
            <motion.p key={depositAddress} initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="break-all font-mono text-sm bg-muted p-3 rounded">{depositAddress ? depositAddress : <Spinner size="sm" className="mx-auto" />}</motion.p>
          </AnimatePresence>

          {depositAddress && (
            <img
              src={`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${encodeURIComponent(depositAddress)}`}
              alt="Deposit QR"
              className="mt-4"
            />
          )}
          <div className="mt-4 pt-4 border-t">
            <p className="text-sm text-muted-foreground mb-2">Dev: simulate a deposit (credits DOGE to your wallet)</p>
            <form onSubmit={handleSimulateDeposit} className="flex flex-wrap items-end gap-2">
              <div className="flex-1 min-w-[120px]">
                <Label htmlFor="simulate-amount" className="sr-only">Amount</Label>
                <Input
                  id="simulate-amount"
                  type="number"
                  min={1}
                  step={1}
                  value={simulateAmount}
                  onChange={(e) => setSimulateAmount(Number(e.target.value) || 0)}
                />
              </div>
              <Button type="submit" variant="secondary" size="sm" disabled={simulateLoading || simulateAmount < 1}>
                {simulateLoading ? "Adding…" : "Add test DOGE"}
              </Button>
            </form>
            {simulateError && <p className="text-sm text-destructive mt-1">{simulateError}</p>}
          </div>
        </div>
        <div className="rounded-lg border bg-card p-6">
          <h2 className="font-semibold mb-4">Withdraw</h2>
          <form onSubmit={handleWithdraw} className="space-y-4">
            <div>
              <Label htmlFor="withdraw-address">Destination Address</Label>
              <Input id="withdraw-address" value={address} onChange={(e) => setAddress(e.target.value)} required />
            </div>
            <PriceInput
              id="withdraw-amount"
              label="Amount"
              value={amount}
              onChange={setAmount}
              min={0}
            />
            {withdrawError && <p className="text-sm text-destructive">{withdrawError}</p>}
            <Button type="submit" disabled={withdrawLoading}>{withdrawLoading ? "Processing..." : "Withdraw"}</Button>
          </form>
        </div>
      </div>
      <div className="rounded-lg border overflow-hidden">
        <h2 className="font-semibold p-4 border-b">Transaction History</h2>
        <AnimatePresence mode="wait">
          {loading ? <motion.div key="loading" initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="p-4 flex items-center justify-center"><Spinner size="sm" /></motion.div> :

            <motion.table key="history" initial={fade_out_scale_1} animate={normalize} exit={fade_out_scale_1} transition={transition_fast} className="w-full text-sm">
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
                      <span className="inline-flex items-center gap-0.5">
                        {Number(entry.credit) > 0 ? "+" : "-"}
                        <DogeIcon size={14} />
                        {formatDogeWithUsd(Number(Number(entry.credit) > 0 ? entry.credit : entry.debit), dogeRate)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </motion.table>}
        </AnimatePresence>
      </div>
    </div>
  );
}
