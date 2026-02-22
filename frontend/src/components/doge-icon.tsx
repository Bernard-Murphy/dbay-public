import dogeImage from "@/assets/dogecoin.webp";

interface DogeIconProps {
  className?: string;
  size?: number;
}

export function DogeIcon({ className, size = 20 }: DogeIconProps) {
  return (
    <img
      src={dogeImage}
      alt="DOGE"
      className={className}
      width={size}
      height={size}
      style={{ display: "inline-block", verticalAlign: "middle" }}
    />
  );
}
