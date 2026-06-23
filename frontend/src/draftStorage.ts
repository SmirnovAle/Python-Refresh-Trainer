const DRAFT_PREFIX = "trainer:draft:";

export function draftKey(exerciseId: number): string {
  return `${DRAFT_PREFIX}${exerciseId}`;
}

export function readDraft(exerciseId: number): string | null {
  try {
    return localStorage.getItem(draftKey(exerciseId));
  } catch {
    return null;
  }
}

export function writeDraft(exerciseId: number, code: string): void {
  try {
    localStorage.setItem(draftKey(exerciseId), code);
  } catch {
    // localStorage недоступен — игнорируем
  }
}

export function clearDraft(exerciseId: number): void {
  try {
    localStorage.removeItem(draftKey(exerciseId));
  } catch {
    // ignore
  }
}

export function resolveInitialCode(
  exerciseId: number,
  lastCode: string | null,
  starterCode: string,
): string {
  if (lastCode && lastCode !== starterCode) {
    return lastCode;
  }
  const draft = readDraft(exerciseId);
  if (draft) {
    return draft;
  }
  return starterCode;
}
