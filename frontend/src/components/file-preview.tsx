import { useRef, useState, useEffect } from "react";
import { Play } from "lucide-react";

interface FilePreviewProps {
  file: File;
  className?: string;
}

/** Image or video preview for a selected file (object URL). */
export function FilePreview({ file, className = "" }: FilePreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [objectUrl, setObjectUrl] = useState<string>("");
  const isVideo = file.type.startsWith("video/");

  useEffect(() => {
    const url = URL.createObjectURL(file);
    setObjectUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);

  if (isVideo) {
    return (
      <div className={`relative w-20 h-20 flex-shrink-0 rounded overflow-hidden bg-muted ${className}`}>
        <video
          ref={videoRef}
          src={objectUrl}
          className="w-full h-full object-cover"
          muted
          playsInline
          preload="metadata"
        />
        <button
          type="button"
          onClick={() => videoRef.current?.play().catch(() => { })}
          className="absolute inset-0 flex items-center justify-center bg-black/30 hover:bg-black/40 transition-colors"
        >
          <Play className="h-8 w-8 text-white" />
        </button>
      </div>
    );
  }

  return (
    <div className={`w-20 h-20 flex-shrink-0 rounded overflow-hidden bg-muted ${className}`}>
      <img src={objectUrl} alt="" className="w-full h-full object-cover" />
    </div>
  );
}
