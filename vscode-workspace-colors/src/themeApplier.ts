import * as vscode from 'vscode';

/**
 * Apply color customizations to workspace settings.
 */
export async function applyTheme(colorCustomizations: Record<string, string>): Promise<void> {
  const config = vscode.workspace.getConfiguration('workbench');

  // Get existing color customizations and merge with new ones
  const existingCustomizations = config.get<Record<string, string>>('colorCustomizations') || {};

  // Remove our managed keys first, then add new ones
  const managedKeys = [
    'titleBar.activeBackground',
    'titleBar.activeForeground',
    'titleBar.inactiveBackground',
    'titleBar.inactiveForeground',
    'titleBar.border',
    'statusBar.background',
    'statusBar.foreground',
    'statusBar.debuggingBackground',
    'statusBar.debuggingForeground',
    'activityBar.background',
    'activityBar.foreground',
    'tab.activeBorder',
  ];

  const cleanedCustomizations: Record<string, string> = {};
  for (const [key, value] of Object.entries(existingCustomizations)) {
    if (!managedKeys.includes(key)) {
      cleanedCustomizations[key] = value;
    }
  }

  // Merge with new customizations
  const newCustomizations = {
    ...cleanedCustomizations,
    ...colorCustomizations,
  };

  await config.update('colorCustomizations', newCustomizations, vscode.ConfigurationTarget.Workspace);
}

/**
 * Clear workspace color theme (remove our managed color customizations).
 */
export async function clearTheme(): Promise<void> {
  const config = vscode.workspace.getConfiguration('workbench');
  const existingCustomizations = config.get<Record<string, string>>('colorCustomizations') || {};

  const managedKeys = [
    'titleBar.activeBackground',
    'titleBar.activeForeground',
    'titleBar.inactiveBackground',
    'titleBar.inactiveForeground',
    'titleBar.border',
    'statusBar.background',
    'statusBar.foreground',
    'statusBar.debuggingBackground',
    'statusBar.debuggingForeground',
    'activityBar.background',
    'activityBar.foreground',
    'tab.activeBorder',
  ];

  const cleanedCustomizations: Record<string, string> = {};
  for (const [key, value] of Object.entries(existingCustomizations)) {
    if (!managedKeys.includes(key)) {
      cleanedCustomizations[key] = value;
    }
  }

  if (Object.keys(cleanedCustomizations).length === 0) {
    await config.update('colorCustomizations', undefined, vscode.ConfigurationTarget.Workspace);
  } else {
    await config.update('colorCustomizations', cleanedCustomizations, vscode.ConfigurationTarget.Workspace);
  }
}
