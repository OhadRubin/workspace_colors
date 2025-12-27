import * as vscode from 'vscode';
import { ThemeTreeProvider, ThemeItem } from './themeProvider';
import { applyTheme, clearTheme } from './themeApplier';

export function activate(context: vscode.ExtensionContext) {
  console.log('Workspace Colors extension is now active');

  // Create and register the tree view provider
  const themeProvider = new ThemeTreeProvider(context.extensionPath);

  const treeView = vscode.window.createTreeView('workspaceColors', {
    treeDataProvider: themeProvider,
    showCollapseAll: true,
  });

  // Register command to apply a theme (called from TreeView)
  const applyThemeCommand = vscode.commands.registerCommand(
    'workspaceColors.applyTheme',
    async (item?: ThemeItem) => {
      if (!item) {
        // Called from command palette - redirect to quick pick
        await vscode.commands.executeCommand('workspaceColors.pickTheme');
        return;
      }
      const colorCustomizations = themeProvider.getColorCustomizations(item);
      if (colorCustomizations) {
        await applyTheme(colorCustomizations);
        vscode.window.showInformationMessage(`Applied "${item.name}" workspace theme`);
      }
    }
  );

  // Register command to pick a theme via quick pick
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

      // Build quick pick items
      const items: vscode.QuickPickItem[] = [];
      for (const [category, categoryColors] of Object.entries(colors)) {
        const formattedCategory = category
          .split('_')
          .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
          .join(' ');

        for (const [name, hex] of Object.entries(categoryColors)) {
          const formattedName = name
            .split('_')
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ');

          items.push({
            label: `$(circle-filled) ${formattedName}`,
            description: hex,
            detail: formattedCategory,
          });
        }
      }

      const selected = await vscode.window.showQuickPick(items, {
        placeHolder: 'Select a workspace color theme',
        matchOnDescription: true,
        matchOnDetail: true,
      });

      if (selected && selected.description) {
        const { generateBrightVersion, generateColorCustomizations } = await import('./colorUtils');
        const baseColor = selected.description;
        const brightColor = generateBrightVersion(baseColor, 25);
        const colorCustomizations = generateColorCustomizations(baseColor, brightColor);
        await applyTheme(colorCustomizations);
        vscode.window.showInformationMessage(`Applied "${selected.label.replace('$(circle-filled) ', '')}" workspace theme`);
      }
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

  context.subscriptions.push(treeView, applyThemeCommand, pickThemeCommand, clearThemeCommand);
}

export function deactivate() {
  // Cleanup if needed
}
