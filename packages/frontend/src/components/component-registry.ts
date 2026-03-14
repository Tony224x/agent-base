import type { LitElement } from 'lit';
import type { ComponentType } from '../types/contracts.js';

type LitElementConstructor = new (...args: unknown[]) => LitElement;

const registry = new Map<ComponentType, LitElementConstructor>();

/**
 * Register a Lit element constructor for a given component type.
 * Subsequent calls with the same type will overwrite the previous entry,
 * which allows consumers to replace built-in renderers.
 */
export function registerComponent(
  type: ComponentType,
  component: LitElementConstructor,
): void {
  registry.set(type, component);
}

/**
 * Retrieve the Lit element constructor for a given component type.
 * Returns `undefined` if nothing has been registered for that type.
 */
export function getComponent(
  type: ComponentType,
): LitElementConstructor | undefined {
  return registry.get(type);
}

/**
 * Check whether a renderer exists for the given component type.
 */
export function hasComponent(type: ComponentType): boolean {
  return registry.has(type);
}
