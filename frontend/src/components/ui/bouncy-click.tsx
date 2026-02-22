"use client";

import { useState } from "react";

interface Ripple {
  id: number;
  x: number;
  y: number;
}

interface BouncyClickProps {
  noRipple?: boolean;
  children: React.ReactNode;
  className?: string;
  disabled?: boolean;
  noBounce?: boolean;
}

const BouncyClick = ({
  noBounce,
  children,
  className,
  noRipple,
  disabled,
}: BouncyClickProps) => {
  const [ripples, setRipples] = useState<Ripple[]>([]);
  const [pressing, setPressing] = useState(false);

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (disabled) return;

    if (!noBounce)
      setPressing(true);

    const button = e.currentTarget;
    const rect = button.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const rippleId = Date.now();
    if (!noRipple) {
      setRipples((prev) => [...prev, { id: rippleId, x, y }]);

      // Remove ripple after animation
      setTimeout(() => {
        setRipples((prev) =>
          prev.filter((ripple: Ripple) => ripple.id !== rippleId)
        );
      }, 600);
    }

    if (!noBounce)
      setTimeout(() => {
        setPressing(false);
      }, 150);
  };

  return (
    <div
      className={`relative overflow-hidden duration-200 transition-all ${!disabled ? "cursor-pointer" : ""
        } ${pressing ? "scale-95" : ""} ${className || ""}`}
      onClick={handleClick}
    >
      {children}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="ripple"
          style={{
            left: ripple.x + "px",
            top: ripple.y + "px",
          }}
        />
      ))}
    </div>
  );
};

export default BouncyClick;
