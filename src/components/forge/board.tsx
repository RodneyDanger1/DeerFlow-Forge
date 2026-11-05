import { useEffect, useState } from "react";
import { Play } from "lucide-react";
import { FAMILIES, buildPlan, type FamilyId } from "@/lib/blueprint/model";

type Props = {
  family: FamilyId;
  onFamily: (id: FamilyId) => void;
  traceFails: boolean;
  onTraceFails: (value: boolean) => void;
  docker: boolean;
  onDocker: (value: boolean) => void;
};

export function Board({ family, onFamily, traceFails, onTraceFails, docker, onDocker }: Props) {
  const plan = buildPlan(family, traceFails, docker);
  const [cursor, setCursor] = useState(-1);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    setCursor(-1);
    setPlaying(false);
  }, [family, traceFails, docker]);

  useEffect(() => {
    if (!playing) return;
    if (cursor >= plan.length) {
      setPlaying(false);
      return;
    }
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const timer = window.setTimeout(() => setCursor((current) => current + 1), reduce ? 0 : 320);
    return () => window.clearTimeout(timer);
  }, [playing, cursor, plan.length]);

  const done = cursor >= plan.length;
  const runLabel = playing ? "Running" : done ? "Run again" : "Run route";

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h2 className="text-xl font-medium">One asset, one route</h2>
        <p className="mt-1 max-w-3xl text-sm text-pretty text-muted">
          Commands are the tuples in routes.py, resolved against the example products.json.
          Fourthwall is the three-step upload in fourthwall.py, not a single POST to /media.
        </p>
      </div>

      <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Product route">
        {FAMILIES.map((item) => {
          const selected = item.id === family;
          return (
            <button
              key={item.id}
              type="button"
              role="radio"
              aria-checked={selected}
              className={
                "h-11 px-3 text-sm transition-colors duration-150 " +
                (selected
                  ? "bg-brass text-bg"
                  : "border border-fg/15 text-fg hover:border-brass")
              }
              onClick={() => onFamily(item.id)}
            >
              {item.name}
            </button>
          );
        })}
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Toggle on={traceFails} onClick={() => onTraceFails(!traceFails)} label="Vector trace exits 1" />
        <Toggle on={docker} onClick={() => onDocker(!docker)} label="Docker sandbox" />
        <button
          type="button"
          disabled={playing}
          className="inline-flex h-11 items-center gap-2 bg-brass px-4 text-sm font-medium text-bg transition-opacity duration-150 disabled:opacity-60"
          onClick={() => {
            setCursor(0);
            setPlaying(true);
          }}
        >
          <Play className="size-4" aria-hidden="true" />
          {runLabel}
        </button>
      </div>
      <p className="-mt-2 text-xs text-muted">
        Simulation of the documented route — no Craft process runs.
      </p>

      <ol className="border border-fg/10" aria-live="polite">
        {plan.map((step, index) => {
          const state = cursor < 0 ? "pending" : index < cursor ? "done" : index === cursor && playing ? "running" : "pending";
          const showResult = state === "done";
          return (
            <li key={step.id} className="grid gap-1 border-b border-fg/10 p-3 last:border-b-0 md:grid-cols-[3rem_1fr]">
              <span
                className={
                  "font-mono text-xs tabular-nums " +
                  (state === "running" ? "text-brass motion-safe:animate-pulse" : showResult && !step.failed ? "text-brass" : "text-muted")
                }
              >
                {String(index + 1).padStart(2, "0")}
              </span>
              <div className="min-w-0">
                <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                  <span className="text-sm font-medium">{step.title}</span>
                  <span className="font-mono text-xs text-muted">{step.module}</span>
                  <span className="font-mono text-xs text-muted">{step.sandbox}</span>
                  {showResult && step.failed ? (
                    <span className="font-mono text-xs text-fg">FAIL</span>
                  ) : null}
                </div>
                <p className="mt-1 overflow-x-auto font-mono text-xs break-all text-fg md:break-normal">{step.command}</p>
                <p className="mt-1 text-sm text-muted">{showResult ? step.result : step.note}</p>
              </div>
            </li>
          );
        })}
      </ol>

      {done ? (
        <p className="text-sm text-muted">
          {traceFails ? "trace_state raster_fallback." : "trace_state traced."}{" "}
          publish_state stays draft unless the account has auto_publish.
        </p>
      ) : null}
    </div>
  );
}

function Toggle({ on, onClick, label }: { on: boolean; onClick: () => void; label: string }) {
  return (
    <button
      type="button"
      aria-pressed={on}
      className={
        "h-11 border px-3 text-sm transition-colors duration-150 " +
        (on ? "border-brass text-brass" : "border-fg/15 text-fg hover:border-brass")
      }
      onClick={onClick}
    >
      {label}
    </button>
  );
}
