/**
 * Presentation-only cleanup for RAG assistant messages (does not change stored content).
 * Matches patterns from datasheet PDF extraction that read poorly in chat.
 */
const INDEXED_PREFIX = /^based on indexed company documents:\s*/i;

/** ST doc header often prepended to every chunk: "DS8626 Rev 12 35/206 ..." */
const ST_SHEET_HEADER =
  /^DS\d{4,6}\s+Rev\s+\d+\s+\d+\/\d+\s+(?:\d+\/\d+\s+)?(?:STM32F\d{3}xx,?\s*STM32F\d{3}xx,?\s*)?/i;

export function stripIndexedAttribution(text: string): { body: string; hadPrefix: boolean } {
  const hadPrefix = INDEXED_PREFIX.test(text);
  let body = text.replace(INDEXED_PREFIX, "").trim();
  return { body, hadPrefix };
}

/**
 * Remove repeated datasheet revision banners at the start so the answer leads with substance.
 */
export function stripLeadingDatasheetBanner(body: string): string {
  let t = body.trim();
  if (ST_SHEET_HEADER.test(t)) {
    t = t.replace(ST_SHEET_HEADER, "").trim();
  }
  return t;
}

export function formatAssistantReplyForDisplay(raw: string): {
  body: string;
  hadIndexedPrefix: boolean;
} {
  const { body: b0, hadPrefix } = stripIndexedAttribution(raw);
  const body = stripLeadingDatasheetBanner(b0);
  return { body, hadIndexedPrefix: hadPrefix };
}
