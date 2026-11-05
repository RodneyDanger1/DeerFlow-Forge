import { ASSUMPTIONS, FAMILIES, type FamilyId } from "@/lib/blueprint/model";

export function RoutesView({ family, onFamily }: { family: FamilyId; onFamily: (id: FamilyId) => void }) {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <h2 className="text-xl font-medium">Fourthwall routes</h2>
        <p className="mt-1 max-w-3xl text-sm text-pretty text-muted">
          routes.py is the only file that knows Craft flags. A flag change is one tuple, not a hunt through the orchestrator.
        </p>
      </div>
      <div className="flex flex-col gap-3">
        {FAMILIES.map((item) => {
          const open = item.id === family;
          return (
            <section key={item.id} className={"border " + (open ? "border-brass" : "border-fg/10")}>
              <button
                type="button"
                className="flex w-full flex-col gap-1 p-3 text-left md:flex-row md:items-baseline md:justify-between"
                aria-expanded={open}
                onClick={() => onFamily(item.id)}
              >
                <span className="text-base font-medium">{item.name}</span>
                <span className="text-sm text-muted">{item.focus}</span>
              </button>
              {open ? (
                <div className="flex flex-col gap-3 border-t border-fg/10 p-3">
                  <p className="text-sm">{item.blanks}</p>
                  <p className="font-mono text-xs text-muted">
                    trace {item.traceExtra ? `+ ${item.traceExtra}` : "with no extra flags"} · upload {item.upload}
                  </p>
                  <ol className="flex flex-col gap-3">
                    {item.steps.map((step, index) => (
                      <li key={step.name}>
                        <p className="text-sm">
                          <span className="font-mono text-xs text-brass">{String(index + 1).padStart(2, "0")}</span>{" "}
                          {step.name}
                          <span className="text-muted"> · {step.module}</span>
                          {step.validator ? <span className="text-muted"> · {step.validator}</span> : null}
                          {step.timeout ? <span className="text-muted"> · timeout {step.timeout}</span> : null}
                        </p>
                        <p className="mt-1 overflow-x-auto font-mono text-xs break-all text-fg md:break-normal">{step.command}</p>
                        <p className="mt-1 font-mono text-xs text-muted">{step.output}</p>
                      </li>
                    ))}
                  </ol>
                  {item.note ? <p className="text-sm text-pretty text-muted">{item.note}</p> : null}
                </div>
              ) : null}
            </section>
          );
        })}
      </div>
      <section>
        <h3 className="text-base font-medium">Assumptions the route file already marks</h3>
        <ul className="mt-2 flex flex-col gap-2">
          {ASSUMPTIONS.map((item) => (
            <li key={item} className="border-l border-brass pl-3 text-sm text-pretty text-muted">
              {item}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
