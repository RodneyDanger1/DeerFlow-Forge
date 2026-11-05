import { useState } from "react";
import { Check, Copy, Download, X } from "lucide-react";
import { copyText, downloadText } from "@/lib/blueprint/clipboard";

export function CopyButton({ text, label = "Copy" }: { text: string; label?: string }) {
  const [status, setStatus] = useState<"idle" | "copied" | "failed">("idle");
  return (
    <button
      type="button"
      className="inline-flex h-11 items-center gap-2 border border-fg/15 px-3 text-sm text-fg transition-colors duration-150 hover:border-brass hover:text-brass"
      onClick={() => {
        void copyText(text).then((ok) => {
          setStatus(ok ? "copied" : "failed");
          window.setTimeout(() => setStatus("idle"), 1600);
        });
      }}
    >
      {status === "copied" ? (
        <Check className="size-4" aria-hidden="true" />
      ) : status === "failed" ? (
        <X className="size-4" aria-hidden="true" />
      ) : (
        <Copy className="size-4" aria-hidden="true" />
      )}
      {status === "copied" ? "Copied" : status === "failed" ? "Copy failed" : label}
    </button>
  );
}

export function DownloadButton({ filename, text }: { filename: string; text: string }) {
  return (
    <button
      type="button"
      className="inline-flex h-11 items-center gap-2 border border-fg/15 px-3 text-sm text-fg transition-colors duration-150 hover:border-brass hover:text-brass"
      onClick={() => downloadText(filename, text)}
    >
      <Download className="size-4" aria-hidden="true" />
      Download
    </button>
  );
}
