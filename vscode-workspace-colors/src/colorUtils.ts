/**
 * Color utility functions for HSL/Hex conversion.
 * Ported from generate.py
 */

export interface HSL {
  h: number; // 0-360
  s: number; // 0-100
  l: number; // 0-100
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
 * Ported from generate.py lines 23-27
 */
export function generateBrightVersion(hexColor: string, lightnessBoost: number = 25): string {
  const { h, s, l } = hexToHsl(hexColor);
  const newL = Math.min(100, l + lightnessBoost);
  return hslToHex(h, s, newL);
}

/**
 * Generate VS Code color customizations for a theme.
 * Ported from generate.py lines 30-41
 */
export function generateColorCustomizations(baseColor: string, brightColor: string): Record<string, string> {
  return {
    'titleBar.activeBackground': baseColor,
    'titleBar.inactiveBackground': brightColor,
    'titleBar.border': brightColor,
    'statusBar.background': brightColor,
    'statusBar.debuggingBackground': brightColor,
    'tab.activeBorder': brightColor,
  };
}
