import {
  Car,
  Shirt,
  Smartphone,
  Home,
  CircleDot,
  Gamepad2,
  BookOpen,
  Star,
  Gem,
  FolderOpen,
  LucideIcon,
} from "lucide-react";

const ICON_MAP: Record<string, LucideIcon> = {
  car: Car,
  shirt: Shirt,
  smartphone: Smartphone,
  home: Home,
  "circle-dot": CircleDot,
  "gamepad-2": Gamepad2,
  "book-open": BookOpen,
  star: Star,
  gem: Gem,
};

interface CategoryIconProps {
  defaultIcon?: string;
  iconUrl?: string | null;
  className?: string;
  size?: number;
}

/** Renders category icon from default_icon (Lucide) or icon_url. Falls back to FolderOpen. */
export function CategoryIcon({ defaultIcon, iconUrl, className, size = 24 }: CategoryIconProps) {
  if (iconUrl) {
    return (
      <img
        src={iconUrl}
        alt=""
        className={className}
        width={size}
        height={size}
        style={{ display: "inline-block", verticalAlign: "middle" }}
      />
    );
  }
  const IconComponent = defaultIcon ? ICON_MAP[defaultIcon] : null;
  if (IconComponent) {
    return <IconComponent className={className} size={size} />;
  }
  return <FolderOpen className={className} size={size} />;
}
