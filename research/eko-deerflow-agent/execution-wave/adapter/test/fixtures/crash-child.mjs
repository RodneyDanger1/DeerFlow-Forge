/**
 * Crash fixture: die after the app has applied the effect, before the pipeline
 * records the result. Exit code 9 is the contract the test asserts on.
 *
 * This is a deliberate process kill, not a simulated one: the session on disk
 * is whatever the FileStore really committed at that instant.
 */

import { Conductor } from '../../src/machine.mjs';
import { allowAllPolicy, createDocumentVerifier } from '../../src/ports.mjs';
import { FileStore } from '../../src/store.mjs';
import { FileCraftPort } from './file-craft-port.mjs';

const directory = process.argv[2];
if (!directory) {
  process.stderr.write('usage: crash-child.mjs <session-directory>\n');
  process.exit(2);
}

const port = new FileCraftPort(directory);
const conductor = new Conductor({
  store: new FileStore(directory),
  ports: {
    craft: port,
    approval: allowAllPolicy(),
    verify: createDocumentVerifier({ port }),
  },
  episodeId: 'ep-crash',
  plan: [
    {
      planStepId: 'add-layer',
      commandId: 'craft://document/add-layer',
      args: { name: 'Ink' },
      capabilityProfile: 'edit',
      postconditions: [{ kind: 'layer-count', equals: 1 }],
    },
  ],
  hooks: {
    afterExecute: async () => {
      // The effect is on disk by now; the result is not recorded.
      process.exit(9);
    },
  },
});

await conductor.open();
await conductor.run();

// Reaching this line means the hook never ran, which the test treats as failure.
process.exit(0);
