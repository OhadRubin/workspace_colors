import * as vscode from 'vscode';
import { applyTheme, clearTheme } from './themeApplier';
import { generateBrightVersion, generateColorCustomizations } from './colorUtils';

interface ColorQuickPickItem extends vscode.QuickPickItem {
  baseColor?: string;
}

/**
 * Generate an SVG data URI for a colored square icon.
 */
function createColorSwatchUri(baseColor: string, brightColor: string): vscode.Uri {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
    <rect x="0" y="0" width="8" height="16" fill="${baseColor}" rx="2"/>
    <rect x="8" y="0" width="8" height="16" fill="${brightColor}" rx="2"/>
  </svg>`;
  const encoded = Buffer.from(svg).toString('base64');
  return vscode.Uri.parse(`data:image/svg+xml;base64,${encoded}`);
}

function formatName(name: string): string {
  return name
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

export function activate(context: vscode.ExtensionContext) {
  console.log('Workspace Colors extension is now active');

  // Register command to pick a theme via quick pick with live preview
  const pickThemeCommand = vscode.commands.registerCommand(
    'workspaceColors.pickTheme',
    async () => {
      // Load colors for quick pick
      const colorsPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'colors.json');
      const colorsContent = await vscode.workspace.fs.readFile(colorsPath);
      const colors = JSON.parse(Buffer.from(colorsContent).toString('utf-8')) as Record<
        string,
        Record<string, string>
      >;

      // Build quick pick items with category separators
      const items: ColorQuickPickItem[] = [];
      for (const [category, categoryColors] of Object.entries(colors)) {
        // Add category separator
        items.push({
          label: formatName(category),
          kind: vscode.QuickPickItemKind.Separator,
        });

        // Add colors in this category
        for (const [name, hex] of Object.entries(categoryColors)) {
          const brightColor = generateBrightVersion(hex, 25);
          items.push({
            label: formatName(name),
            description: hex,
            iconPath: createColorSwatchUri(hex, brightColor),
            baseColor: hex,
          });
        }
      }

      // Use createQuickPick for live preview on navigation
      const quickPick = vscode.window.createQuickPick<ColorQuickPickItem>();
      quickPick.items = items;
      quickPick.placeholder = 'Select a workspace color theme';
      quickPick.matchOnDescription = true;

      // Live preview as user navigates
      quickPick.onDidChangeActive(async (activeItems) => {
        if (activeItems.length > 0 && activeItems[0].baseColor) {
          const item = activeItems[0];
          const brightColor = generateBrightVersion(item.baseColor!, 25);
          const colorCustomizations = generateColorCustomizations(item.baseColor!, brightColor);
          await applyTheme(colorCustomizations);
        }
      });

      // Handle selection
      quickPick.onDidAccept(async () => {
        const selected = quickPick.selectedItems[0];
        if (selected && selected.baseColor) {
          vscode.window.showInformationMessage(`Applied "${selected.label}" workspace theme`);
        }
        quickPick.hide();
      });

      quickPick.onDidHide(() => quickPick.dispose());
      quickPick.show();
    }
  );

  // Register command to clear theme
  const clearThemeCommand = vscode.commands.registerCommand(
    'workspaceColors.clearTheme',
    async () => {
      await clearTheme();
      vscode.window.showInformationMessage('Cleared workspace color theme');
    }
  );

  context.subscriptions.push(pickThemeCommand, clearThemeCommand);
}

export function deactivate() {
  // Cleanup if needed
}
