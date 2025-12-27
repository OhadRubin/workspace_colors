import * as vscode from 'vscode';
import { applyTheme, clearTheme } from './themeApplier';
import { generateBrightVersion, generateColorCustomizations } from './colorUtils';

function formatName(name: string): string {
  return name
    .split('_')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

function getWebviewContent(colors: Record<string, Record<string, string>>, currentColor: string | undefined): string {
  let categoriesHtml = '';

  for (const [category, categoryColors] of Object.entries(colors)) {
    let colorsHtml = '';
    for (const [name, hex] of Object.entries(categoryColors)) {
      const brightColor = generateBrightVersion(hex, 25);
      const isSelected = currentColor === hex ? ' selected' : '';
      colorsHtml += `
        <div class="color-item${isSelected}" data-color="${hex}" title="${formatName(name)} - ${hex}">
          <div class="color-swatch">
            <div class="color-half" style="background: ${hex}"></div>
            <div class="color-half" style="background: ${brightColor}"></div>
          </div>
          <span class="color-name">${formatName(name)}</span>
        </div>
      `;
    }

    categoriesHtml += `
      <div class="category">
        <h2 class="category-title">${formatName(category)}</h2>
        <div class="color-grid">${colorsHtml}</div>
      </div>
    `;
  }

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Workspace Colors</title>
  <style>
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: var(--vscode-font-family);
      background: var(--vscode-editor-background);
      color: var(--vscode-editor-foreground);
      padding: 16px;
    }

    h1 {
      font-size: 1.4em;
      margin-bottom: 16px;
      font-weight: 500;
    }

    .toolbar {
      display: flex;
      gap: 8px;
      margin-bottom: 20px;
      position: sticky;
      top: 0;
      background: var(--vscode-editor-background);
      padding: 12px 0;
      z-index: 100;
      border-bottom: 1px solid var(--vscode-widget-border);
    }

    button {
      background: var(--vscode-button-background);
      color: var(--vscode-button-foreground);
      border: none;
      padding: 6px 14px;
      border-radius: 4px;
      cursor: pointer;
      font-size: 13px;
    }

    button:hover {
      background: var(--vscode-button-hoverBackground);
    }

    button.secondary {
      background: var(--vscode-button-secondaryBackground);
      color: var(--vscode-button-secondaryForeground);
    }

    button .btn-swatch {
      display: inline-block;
      width: 12px;
      height: 12px;
      border-radius: 2px;
      margin-right: 6px;
      vertical-align: middle;
      box-shadow: 0 0 0 1px rgba(255,255,255,0.2);
    }

    button:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .category {
      margin-bottom: 24px;
    }

    .category-title {
      font-size: 0.85em;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--vscode-descriptionForeground);
      margin-bottom: 10px;
      padding-bottom: 6px;
      border-bottom: 1px solid var(--vscode-widget-border);
    }

    .color-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
      gap: 8px;
    }

    .color-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 8px;
      border-radius: 6px;
      cursor: pointer;
      transition: background 0.15s;
    }

    .color-item:hover {
      background: var(--vscode-list-hoverBackground);
    }

    .color-swatch {
      width: 28px;
      height: 28px;
      border-radius: 4px;
      display: flex;
      overflow: hidden;
      flex-shrink: 0;
      box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }

    .color-half {
      flex: 1;
    }

    .color-name {
      font-size: 12px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .selected {
      background: var(--vscode-list-activeSelectionBackground);
      color: var(--vscode-list-activeSelectionForeground);
    }

    .previewing {
      outline: 2px solid var(--vscode-focusBorder);
      outline-offset: -2px;
    }
  </style>
</head>
<body>
  <h1>Workspace Colors</h1>
  <div class="toolbar">
    <button id="saveBtn"><span class="btn-swatch" id="saveSwatch"></span>Save</button>
    <button id="clearBtn" class="secondary"><span class="btn-swatch" id="clearSwatch"></span>Clear</button>
    <button id="restoreDefaultBtn" class="secondary">Restore Default</button>
  </div>
  <div id="categories">${categoriesHtml}</div>

  <script>
    const vscode = acquireVsCodeApi();
    // savedColor = what's actually committed to settings
    let savedColor = document.querySelector('.color-item.selected')?.dataset.color || null;
    // clickedColor = what user clicked on (pending save), defaults to savedColor
    let clickedColor = savedColor;
    // previewColor = what we're currently previewing (may differ during hover)
    let previewColor = savedColor;

    function updateUI() {
      document.querySelectorAll('.color-item').forEach(i => {
        i.classList.toggle('selected', i.dataset.color === savedColor);
        // Show previewing state for clicked color (pending) or hover preview
        i.classList.toggle('previewing', i.dataset.color === clickedColor && clickedColor !== savedColor);
      });

      // Update button swatches
      const saveSwatch = document.getElementById('saveSwatch');
      const clearSwatch = document.getElementById('clearSwatch');
      const saveBtn = document.getElementById('saveBtn');
      const clearBtn = document.getElementById('clearBtn');

      // Save button shows clickedColor (what will be saved)
      if (clickedColor) {
        saveSwatch.style.background = clickedColor;
        saveSwatch.style.display = 'inline-block';
        saveBtn.disabled = false;
      } else {
        saveSwatch.style.display = 'none';
        saveBtn.disabled = true;
      }

      // Clear button shows savedColor (what it will restore to)
      if (savedColor) {
        clearSwatch.style.background = savedColor;
        clearSwatch.style.display = 'inline-block';
      } else {
        clearSwatch.style.display = 'none';
      }
    }

    // Initialize button swatches on load
    updateUI();

    // Handle color clicks - select as pending color
    document.querySelectorAll('.color-item').forEach(item => {
      item.addEventListener('click', () => {
        clickedColor = item.dataset.color;
        previewColor = item.dataset.color;
        vscode.postMessage({ command: 'previewTheme', color: previewColor });
        updateUI();
      });

      // Live preview on hover
      item.addEventListener('mouseenter', () => {
        previewColor = item.dataset.color;
        vscode.postMessage({ command: 'previewTheme', color: previewColor });
        updateUI();
      });

      // Restore to clicked color (or saved color) on mouse leave
      item.addEventListener('mouseleave', () => {
        // Restore to the clicked color if user has clicked something, otherwise savedColor
        const restoreColor = clickedColor || savedColor;
        previewColor = restoreColor;
        if (restoreColor) {
          vscode.postMessage({ command: 'restoreTheme', color: restoreColor });
        } else {
          vscode.postMessage({ command: 'clearTheme' });
        }
        updateUI();
      });
    });

    // Save button - commit current clicked color
    document.getElementById('saveBtn').addEventListener('click', () => {
      if (clickedColor) {
        savedColor = clickedColor;
        previewColor = clickedColor;
        vscode.postMessage({ command: 'saveTheme', color: savedColor });
        updateUI();
      }
    });

    // Clear button - discard pending selection, restore to saved color
    document.getElementById('clearBtn').addEventListener('click', () => {
      clickedColor = savedColor;
      previewColor = savedColor;
      if (savedColor) {
        vscode.postMessage({ command: 'restoreTheme', color: savedColor });
      } else {
        vscode.postMessage({ command: 'clearTheme' });
      }
      updateUI();
    });

    // Restore Default - remove all colors
    document.getElementById('restoreDefaultBtn').addEventListener('click', () => {
      savedColor = null;
      clickedColor = null;
      previewColor = null;
      vscode.postMessage({ command: 'restoreDefault' });
      updateUI();
    });

    // Scroll to selected item on load
    const selected = document.querySelector('.color-item.selected');
    if (selected) {
      selected.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  </script>
</body>
</html>`;
}

/**
 * Get the current applied color from workspace settings.
 */
function getCurrentColor(): string | undefined {
  const config = vscode.workspace.getConfiguration('workbench');
  const colorCustomizations = config.get<Record<string, string>>('colorCustomizations') || {};
  return colorCustomizations['titleBar.activeBackground'];
}

export function activate(context: vscode.ExtensionContext) {
  console.log('Workspace Colors extension is now active');

  let panel: vscode.WebviewPanel | undefined;

  // Register command to pick a theme
  const pickThemeCommand = vscode.commands.registerCommand(
    'workspaceColors.pickTheme',
    async () => {
      // Load colors
      const colorsPath = vscode.Uri.joinPath(context.extensionUri, 'src', 'colors.json');
      const colorsContent = await vscode.workspace.fs.readFile(colorsPath);
      const colors = JSON.parse(Buffer.from(colorsContent).toString('utf-8')) as Record<
        string,
        Record<string, string>
      >;

      // Get current applied color from settings
      const currentColor = getCurrentColor();

      // Create or show panel
      if (panel) {
        panel.reveal();
      } else {
        panel = vscode.window.createWebviewPanel(
          'workspaceColors',
          'Workspace Colors',
          vscode.ViewColumn.One,
          { enableScripts: true }
        );

        panel.webview.html = getWebviewContent(colors, currentColor);

        // Handle messages from webview
        panel.webview.onDidReceiveMessage(
          async (message) => {
            switch (message.command) {
              case 'saveTheme':
              case 'previewTheme':
              case 'restoreTheme':
                const baseColor = message.color;
                const brightColor = generateBrightVersion(baseColor, 25);
                const colorCustomizations = generateColorCustomizations(baseColor, brightColor);
                await applyTheme(colorCustomizations);
                break;
              case 'clearTheme':
                // Restore to saved (handled by webview sending restoreTheme if there's a saved color)
                await clearTheme();
                break;
              case 'restoreDefault':
                // Remove all workspace colors
                await clearTheme();
                break;
            }
          },
          undefined,
          context.subscriptions
        );

        panel.onDidDispose(() => {
          panel = undefined;
        });
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

  context.subscriptions.push(pickThemeCommand, clearThemeCommand);
}

export function deactivate() {
  // Cleanup if needed
}
