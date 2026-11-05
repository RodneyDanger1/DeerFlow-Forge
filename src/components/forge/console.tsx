import { useState } from "react";
import type { FamilyId } from "@/lib/blueprint/model";
import { Board } from "@/components/forge/board";
import { PlaybookView } from "@/components/forge/playbook-view";
import { RoutesView } from "@/components/forge/routes-view";
import { SandboxView } from "@/components/forge/sandbox-view";
import { SourcesView } from "@/components/forge/sources-view";

type Section = "board" | "routes" | "sandbox" | "playbook" | "sources";

const NAV: { id: Section; label: string }[] = [
  { id: "board", label: "Board" },
  { id: "routes", label: "Routes" },
  { id: "sandbox", label: "Sandbox" },
  { id: "playbook", label: "Playbook" },
  { id: "sources", label: "Sources" },
];

export function Console() {
  const [section, setSection] = useState<Section>("board");
  const [family, setFamily] = useState<FamilyId>("apparel");
  const [traceFails, setTraceFails] = useState(false);
  const [docker, setDocker] = useState(true);
  const [file, setFile] = useState("pod_pipeline/routes.py");

  function openFile(path: string) {
    setFile(path);
    setSection("sources");
  }

  return (
    <div className="min-h-screen bg-bg text-fg">
      <header className="flex items-center justify-between gap-4 border-b border-fg/10 px-4 py-3">
        <div className="flex items-center gap-3">
          <img src="/favicon.svg" alt="" width={32} height={32} className="size-8" />
          <div>
            <p className="text-xs font-medium tracking-wide text-brass">DEERFLOW</p>
            <h1 className="text-lg font-medium leading-tight">Forge</h1>
          </div>
        </div>
        <div className="hidden text-right sm:block">
          <p className="text-sm">pod_pipeline</p>
          <p className="font-mono text-xs text-muted">Static blueprint · no live services</p>
        </div>
      </header>
      <div className="md:flex">
        <nav className="flex gap-2 overflow-x-auto border-b border-fg/10 p-3 md:w-44 md:shrink-0 md:flex-col md:border-r md:border-b-0" aria-label="Sections">
          {NAV.map((item) => {
            const selected = item.id === section;
            return (
              <button
                key={item.id}
                type="button"
                aria-current={selected ? "page" : undefined}
                className={
                  "h-11 shrink-0 border-l-2 px-3 text-left text-sm " +
                  (selected ? "border-brass bg-fg/10 text-fg" : "border-transparent text-muted hover:text-fg")
                }
                onClick={() => setSection(item.id)}
              >
                {item.label}
              </button>
            );
          })}
        </nav>
        <main className="min-w-0 flex-1 p-4">
          {section === "board" ? (
            <Board
              family={family}
              onFamily={setFamily}
              traceFails={traceFails}
              onTraceFails={setTraceFails}
              docker={docker}
              onDocker={setDocker}
            />
          ) : null}
          {section === "routes" ? <RoutesView family={family} onFamily={setFamily} /> : null}
          {section === "sandbox" ? <SandboxView onOpen={openFile} /> : null}
          {section === "playbook" ? <PlaybookView onOpen={openFile} /> : null}
          {section === "sources" ? <SourcesView file={file} onFile={setFile} /> : null}
        </main>
      </div>
    </div>
  );
}
