# PhotoCraft Batch Automation

Auto-generated from the installed 965-command registry (snapshot 2026-11-05). Every row is a real command id; params are abbreviated. Query the full schema with `$PC commands --json`. PhotoCraft input is positional and `--out` must differ from input.

Commands: **20** across 1 groups.

## Coverage

`actions` 20

## `actions` (20)



| id | label | menu | params (synopsis) | notes |
|---|---|---|---|---|
| `actions.assignSet` | Move to Set |  | {"action":name\|index, "set":name\|null} → {action, set}. The set folder the Actions panel shows the action under (what Load Actions fills and Save Actions writes); null takes it out of any s… |  |
| `actions.conditional` | Conditional |  | {"if":condition, "then":action name\|null, "else":action name\|null} → {if, holds, played, ran?, failed?}. Photoshop's Insert Conditional: conditions always\|never\|isOpen\|landscape\|square\|port… |  |
| `actions.delete` | Delete Action |  | {"action":name\|index, "step":index?} → {deleted:name} or {action, deletedStep, steps:count}. step is 0-based, including pending recorded steps. Whole-action deletion is refused while record… |  |
| `actions.dialog` | Toggle Step Dialog |  | {"action":name\|index, "step":index?, "enabled":bool?} → {action, dialogs:[step…]}. The Actions panel's dialog toggle: the desktop shell shows the step's dialog, seeded with its recorded par… |  |
| `actions.get` | Get Action |  | {"action":name\|index} → {name, steps:[[id, params]…], disabled:[step…], dialogs:[step…], set:name\|null, color:str} (steps is the shape file.automate.batch and droplets take; disabled lists … |  |
| `actions.insert` | Insert Step |  | {"action":name\|index, "id":command id, "params":{}?, "at":index?=end} → {action, step, id, steps}. Inserts a step at the 0-based position (Photoshop's Insert Stop… with id actions.stopMessa… |  |
| `actions.list` | List Actions |  | {} → {actions:[{name, steps:count, set:name\|null}], sets:[name…] (every set in panel order, empty ones too), recording:name\|null} |  |
| `actions.load` | Load Actions… |  | {"path":".atn file"?,"data":base64 bytes?,"set":name? (override the file's set name),"replace":bool=true (replace the actions of a set of the same name),"encoding":"auto"\|label="auto" (the … |  |
| `actions.move` | Move Action or Step |  | {"action":name\|index, "step":index?, "to":index}. Move a step within its action, or the action itself. to is the final zero-based index. Pending recorded steps can be moved. |  |
| `actions.newSet` | New Set |  | {"name":str? (default "Set N")} → {set}. An empty set folder in the Actions panel, as Photoshop's New Set… makes; New Action records into the selected set (actions.record's `set`). Save Act… |  |
| `actions.photoshopStep` | Photoshop Step |  | {"event":id,"name":str,"descriptor":base64?} (a step from a .atn file PhotoCraft has no command for: fails at playback, written back by actions.save) |  |
| `actions.play` | Play Action |  | {"action":name\|index, "from":step?} → {action, ran, failed?:{step, id, error}}. step and from are 0-based; steps switched off with actions.toggle are skipped. Stops at the first error (the … |  |
| `actions.record` | Record Action |  | {"name":str? (new action, default "Action N"),"set":name? (the set it goes in, as New Action records into the selected set)} or {"action":name\|index} (append) → {action, index} |  |
| `actions.rename` | Rename Action |  | {"action":name\|index, "name":str} → {action, index}. The name must not be empty or whitespace-only and must be unique. Nested Play Action steps and the action's function key follow the rena… |  |
| `actions.save` | Save Actions… |  | {"path":".atn file"? (else the bytes come back as base64 `data`),"set":name? (that set's actions, none for an empty New Set set; default: every action, as the set "PhotoCraft Actions"),"act… |  |
| `actions.setColor` | Set Action Color |  | {"action":name\|index, "color":""\|"red"\|"orange"\|"yellow"\|"green"\|"blue"\|"violet"\|"gray"} → {action, color}. The Button Mode colour. Empty clears it. |  |
| `actions.setHistory` | Set Actions History |  | {"singleState":bool} → {singleState}. Persist Create a single history state (default true). Playback Options can use this setting without changing its performance mode. |  |
| `actions.stop` | Stop Recording |  | {} → {action, steps:count} (steps recorded since actions.record, queries and action-editing commands omitted) |  |
| `actions.stopMessage` | Stop |  | {"message":str,"allowContinue":bool=false} (Photoshop's Insert Stop: a step that shows the message; headless playback continues when allowContinue is set and otherwise stops the action with… |  |
| `actions.toggle` | Toggle Action Steps |  | {"action":name\|index, "step":index?, "enabled":bool?} → {action, disabled:[step…]}. Switch one 0-based step (including pending recorded steps) on or off for playback, Batch and droplets; om… |  |
