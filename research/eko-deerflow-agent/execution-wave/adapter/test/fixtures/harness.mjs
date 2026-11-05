/**
 * Shared test harness for the adapter prototype.
 * Ports are the real reference doubles from src/ports.mjs; nothing here fakes
 * pipeline logic.
 */

import { Conductor } from '../../src/machine.mjs';
import { allowAllPolicy, createDocumentVerifier, createMemoryCraftPort } from '../../src/ports.mjs';
import { MemoryStore } from '../../src/store.mjs';

export const PLANS = {
  happy: [
    {
      planStepId: 'add-layer',
      commandId: 'craft://document/add-layer',
      args: { name: 'Ink' },
      capabilityProfile: 'edit',
      postconditions: [{ kind: 'layer-count', equals: 1 }],
    },
    {
      planStepId: 'export-png',
      commandId: 'craft://document/export',
      args: { name: 'final.png' },
      capabilityProfile: 'export',
      postconditions: [
        { kind: 'artifact-exists', name: 'final.png' },
        { kind: 'document-flag', flag: 'exported', equals: true },
      ],
    },
  ],
  single: [
    {
      planStepId: 'add-layer',
      commandId: 'craft://document/add-layer',
      args: { name: 'Ink' },
      capabilityProfile: 'edit',
      postconditions: [{ kind: 'layer-count', equals: 1 }],
    },
  ],
};

/** Six distinct add-layer steps; used to make compaction fire. */
export function manyLayerPlan(count = 6) {
  return Array.from({ length: count }, (_, i) => ({
    planStepId: `add-layer-${i + 1}`,
    commandId: 'craft://document/add-layer',
    args: { name: `Layer-${i + 1}` },
    capabilityProfile: 'edit',
    postconditions: [{ kind: 'layer-count', equals: i + 1 }],
  }));
}

export function buildPorts({ craft = {}, approval = allowAllPolicy(), verify = null } = {}) {
  const port = createMemoryCraftPort(craft);
  return {
    port,
    ports: {
      craft: port,
      approval,
      verify: verify ?? createDocumentVerifier({ port }),
    },
  };
}

export async function makeConductor({
  plan = PLANS.single,
  craft = {},
  approval,
  verify,
  config,
  store = new MemoryStore(),
  episodeId = 'ep-test',
  hooks,
  operations,
} = {}) {
  const { ports, port } = buildPorts({ craft, approval, verify });
  const conductor = new Conductor({ store, ports, episodeId, plan, config, hooks, operations });
  await conductor.open();
  return { conductor, port, ports, store };
}

export function eventKinds(conductor) {
  return conductor.state.events.map((event) => event.kind);
}
