import { useState } from "react";
import { Check, Copy, Download } from "lucide-react";
import { copyText, downloadText } from "@/lib/blueprint/clipboard";

export function CopyButton({ text, label = "Copy" }: { text: string; label?: string }) {
  const [done, setDone] = useState(false);
  return (
    <button
      type="button"
      className="inline-flex h-11 items-center gap-2 border border-fg/15 px-3 text-sm text-fg transition-colors duration-150 hover:border-brass hover:text-brass"
      onClick={() => {
        void copyText(text).then((ok) => {
          if (!ok) return;
          setDone(true);
          window.setTimeout(() => setDone(false), 1400);
        });
      }}
    >
      {done ? <Check className="size-4" aria-hidden="true" /> : <Copy className="size-4" aria-hidden="true" />}
      {done ? "Copied" : label}
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
