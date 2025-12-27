/**
 * Color utility functions for HSL/Hex conversion and contrast calculations.
 * Ported from color_picker/base.py
 */

export interface HSL {
  h: number; // 0-360
  s: number; // 0-100
  l: number; // 0-100
}

/**
 * Convert sRGB component to linear RGB.
 */
function srgbToLinear(u: number): number {
  return u <= 0.03928 ? u / 12.92 : Math.pow((u + 0.055) / 1.055, 2.4);
}

/**
 * Calculate relative luminance per WCAG 2.1.
 */
export function relativeLuminance(hexColor: string): number {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;
  const rLin = srgbToLinear(r);
  const gLin = srgbToLinear(g);
  const bLin = srgbToLinear(b);
  return 0.2126 * rLin + 0.7152 * gLin + 0.0722 * bLin;
}

/**
 * Calculate WCAG contrast ratio between two hex colors.
 */
export function contrastRatio(color1: string, color2: string): number {
  const l1 = relativeLuminance(color1);
  const l2 = relativeLuminance(color2);
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Choose black or white foreground based on background luminance.
 */
export function chooseForeground(bgHex: string): string {
  const lum = relativeLuminance(bgHex);
  // Dark bg (lum < 0.4) -> white text, Light bg -> black text
  return lum < 0.4 ? '#ffffff' : '#000000';
}

/**
 * Convert hex color to HSL (hue 0-360, sat 0-100, light 0-100).
 * Ported from generate.py lines 9-14
 */
export function hexToHsl(hexColor: string): HSL {
  const hex = hexColor.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16) / 255;
  const g = parseInt(hex.substring(2, 4), 16) / 255;
  const b = parseInt(hex.substring(4, 6), 16) / 255;

  const max = Math.max(r, g, b);
  const min = Math.min(r, g, b);
  const l = (max + min) / 2;

  let h = 0;
  let s = 0;

  if (max !== min) {
    const d = max - min;
    s = l > 0.5 ? d / (2 - max - min) : d / (max + min);

    switch (max) {
      case r:
        h = ((g - b) / d + (g < b ? 6 : 0)) / 6;
        break;
      case g:
        h = ((b - r) / d + 2) / 6;
        break;
      case b:
        h = ((r - g) / d + 4) / 6;
        break;
    }
  }

  return {
    h: h * 360,
    s: s * 100,
    l: l * 100,
  };
}

/**
 * Convert HSL (hue 0-360, sat 0-100, light 0-100) to hex color.
 * Ported from generate.py lines 17-20
 */
export function hslToHex(h: number, s: number, l: number): string {
  const hNorm = h / 360;
  const sNorm = s / 100;
  const lNorm = l / 100;

  let r: number, g: number, b: number;

  if (sNorm === 0) {
    r = g = b = lNorm;
  } else {
    const hue2rgb = (p: number, q: number, t: number): number => {
      if (t < 0) t += 1;
      if (t > 1) t -= 1;
      if (t < 1 / 6) return p + (q - p) * 6 * t;
      if (t < 1 / 2) return q;
      if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
      return p;
    };

    const q = lNorm < 0.5 ? lNorm * (1 + sNorm) : lNorm + sNorm - lNorm * sNorm;
    const p = 2 * lNorm - q;
    r = hue2rgb(p, q, hNorm + 1 / 3);
    g = hue2rgb(p, q, hNorm);
    b = hue2rgb(p, q, hNorm - 1 / 3);
  }

  const toHex = (x: number): string => {
    const hex = Math.round(x * 255).toString(16);
    return hex.length === 1 ? '0' + hex : hex;
  };

  return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

/**
 * Generate a brighter version of the given color.
 * Uses adaptive lightness boost: more for dark colors, less for light colors.
 * Caps at 75% lightness to maintain visibility against text.
 */
export function generateBrightVersion(hexColor: string, lightnessBoost?: number): string {
  const { h, s, l } = hexToHsl(hexColor);

  if (lightnessBoost === undefined) {
    // Adaptive: dark colors get more boost, light colors less
    // Range roughly: 35 for l=0, 15 for l=60
    lightnessBoost = Math.max(15, 35 - l * 0.33);
  }

  // Cap at 75% to avoid washing out (keeps contrast with text)
  const newL = Math.min(75, l + lightnessBoost);
  return hslToHex(h, s, newL);
}

/**
 * Generate VS Code color customizations for a theme with proper foreground colors.
 */
export function generateColorCustomizations(baseColor: string, brightColor: string): Record<string, string> {
  // Choose foreground colors based on background luminance
  const baseFg = chooseForeground(baseColor);
  const brightFg = chooseForeground(brightColor);

  // Generate a darker version for activity bar (more muted)
  const { h, s, l } = hexToHsl(baseColor);
  const activityBarBg = hslToHex(h, s, Math.max(10, l - 10));
  const activityBarFg = chooseForeground(activityBarBg);

  return {
    // Title bar
    'titleBar.activeBackground': baseColor,
    'titleBar.activeForeground': baseFg,
    'titleBar.inactiveBackground': brightColor,
    'titleBar.inactiveForeground': brightFg,
    'titleBar.border': brightColor,
    // Status bar
    'statusBar.background': brightColor,
    'statusBar.foreground': brightFg,
    'statusBar.debuggingBackground': brightColor,
    'statusBar.debuggingForeground': brightFg,
    // Activity bar
    'activityBar.background': activityBarBg,
    'activityBar.foreground': activityBarFg,
    // Tabs
    'tab.activeBorder': brightColor,
  };
}
