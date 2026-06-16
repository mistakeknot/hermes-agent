import { describe, expect, it } from 'vitest'

import { contrastRatio, luminance } from './color'
import { BUILTIN_THEME_LIST, BUILTIN_THEMES, DEFAULT_TYPOGRAPHY, EMOJI_FALLBACK } from './presets'

// #40364: none of the UI text/mono fonts carry emoji glyphs, so every font
// stack must end with a color-emoji fallback or emoji render as tofu on
// platforms whose default font lacks them (e.g. Linux).
describe('theme typography emoji fallback (#40364)', () => {
  const stacks: Array<[string, string]> = [
    ['DEFAULT_TYPOGRAPHY.fontSans', DEFAULT_TYPOGRAPHY.fontSans],
    ['DEFAULT_TYPOGRAPHY.fontMono', DEFAULT_TYPOGRAPHY.fontMono],
    // A theme may override only fontMono (fontSans then falls back to the
    // default, which already carries the emoji stack), so skip undefined.
    ...BUILTIN_THEME_LIST.flatMap(theme =>
      (
        [
          [`${theme.name}.fontSans`, theme.typography?.fontSans],
          [`${theme.name}.fontMono`, theme.typography?.fontMono]
        ] as Array<[string, string | undefined]>
      ).filter((entry): entry is [string, string] => typeof entry[1] === 'string')
    )
  ]

  it.each(stacks)('%s includes a color-emoji font', (_label, stack) => {
    expect(stack).toMatch(/Apple Color Emoji|Segoe UI Emoji|Noto Color Emoji|(^|,\s*)emoji\b/)
  })

  it('EMOJI_FALLBACK lists the major platform emoji fonts', () => {
    expect(EMOJI_FALLBACK).toContain('Apple Color Emoji')
    expect(EMOJI_FALLBACK).toContain('Segoe UI Emoji')
    expect(EMOJI_FALLBACK).toContain('Noto Color Emoji')
  })
})

describe('built-in desktop themes', () => {
  it('ships the Nousromancer palette as a first-class built-in theme', () => {
    const theme = BUILTIN_THEMES.nousromancer
    const darkColors = theme.darkColors

    expect(BUILTIN_THEME_LIST).toContain(theme)
    expect(theme.label).toBe('Nousromancer')
    expect(darkColors).toBeDefined()
    expect(theme.terminal).toEqual(expect.objectContaining({ foreground: expect.any(String) }))
    expect(theme.darkTerminal).toEqual(expect.objectContaining({ foreground: expect.any(String) }))

    expect(luminance(theme.colors.background)).toBeGreaterThan(0.5)
    expect(luminance(darkColors?.background ?? '#FFFFFF')).toBeLessThanOrEqual(0.5)
    expect(contrastRatio(theme.colors.background, theme.colors.foreground)).toBeGreaterThanOrEqual(4.5)
    expect(
      contrastRatio(darkColors?.background ?? '#000000', darkColors?.foreground ?? '#000000')
    ).toBeGreaterThanOrEqual(4.5)
  })
})
