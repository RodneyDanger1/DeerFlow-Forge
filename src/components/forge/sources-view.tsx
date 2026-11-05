import { SOURCE_GROUPS, SOURCES, type SourceFile } from "@/lib/blueprint/sources";
import { CopyButton, DownloadButton } from "@/components/forge/copy-button";

export function SourcesView({ file, onFile }: { file: string; onFile: (path: string) => void }) {
  const active = SOURCES.find((item) => item.path === file) ?? SOURCES[0];
  return (
    <div className="grid gap-4 md:grid-cols-[16rem_1fr]">
      <div className="min-w-0">
        <label className="mb-3 block md:hidden">
          <span className="mb-1 block text-xs tracking-wide text-muted">Source</span>
          <select
            className="h-11 w-full border border-fg/15 bg-bg px-2 text-sm text-fg"
            value={active.path}
            onChange={(event) => onFile(event.target.value)}
          >
            {SOURCE_GROUPS.map((group) => (
              <optgroup key={group.id} label={group.label}>
                {SOURCES.filter((item) => item.group === group.id).map((item) => (
                  <option key={item.path} value={item.path}>
                    {item.path}
                  </option>
                ))}
              </optgroup>
            ))}
          </select>
        </label>
        <div className="hidden md:block">
          {SOURCE_GROUPS.map((group) => (
            <div key={group.id} className="mb-4">
              <p className="mb-1 text-xs tracking-wide text-muted">{group.label}</p>
              <ul>
                {SOURCES.filter((item) => item.group === group.id).map((item) => (
                  <li key={item.path}>
                    <button
                      type="button"
                      className={
                        "w-full truncate px-2 py-2 text-left font-mono text-xs " +
                        (item.path === active.path ? "bg-fg/10 text-brass" : "text-fg hover:bg-fg/5")
                      }
                      onClick={() => onFile(item.path)}
                    >
                      {item.path.split("/").pop()}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
      <SourcePane file={active} />
    </div>
  );
}

function SourcePane({ file }: { file: SourceFile }) {
  const lines = file.source.split("\n").length;
  const filename = file.path.split("/").pop() ?? file.path;
  return (
    <section className="min-w-0">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="font-mono text-sm">{file.path}</h2>
          <p className="font-mono text-xs text-muted tabular-nums">{lines} lines</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <CopyButton text={file.source} />
          <DownloadButton filename={filename} text={file.source} />
        </div>
      </div>
      <pre className="mt-2 max-h-screen overflow-auto border border-fg/10 p-3 font-mono text-xs leading-relaxed text-fg">{file.source}</pre>
    </section>
  );
}
