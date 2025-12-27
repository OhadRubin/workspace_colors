import * as vscode from 'vscode';
import * as path from 'path';
import { generateBrightVersion, generateColorCustomizations } from './colorUtils';

type ColorCategories = Record<string, Record<string, string>>;

export interface ThemeItem {
  type: 'category' | 'color';
  name: string;
  category?: string;
  baseColor?: string;
}

export class ThemeTreeItem extends vscode.TreeItem {
  constructor(
    public readonly item: ThemeItem,
    public readonly collapsibleState: vscode.TreeItemCollapsibleState
  ) {
    super(item.name, collapsibleState);

    if (item.type === 'color' && item.baseColor) {
      this.description = item.baseColor;
      this.tooltip = `${item.name} - ${item.baseColor}`;
      this.iconPath = new vscode.ThemeIcon('circle-filled', new vscode.ThemeColor('charts.foreground'));
      this.command = {
        command: 'workspaceColors.applyTheme',
        title: 'Apply Theme',
        arguments: [item],
      };
      this.contextValue = 'colorTheme';
    } else {
      this.iconPath = new vscode.ThemeIcon('symbol-color');
      this.contextValue = 'category';
    }
  }
}

export class ThemeTreeProvider implements vscode.TreeDataProvider<ThemeItem> {
  private _onDidChangeTreeData: vscode.EventEmitter<ThemeItem | undefined | null | void> =
    new vscode.EventEmitter<ThemeItem | undefined | null | void>();
  readonly onDidChangeTreeData: vscode.Event<ThemeItem | undefined | null | void> =
    this._onDidChangeTreeData.event;

  private colors: ColorCategories = {};

  constructor(private extensionPath: string) {
    this.loadColors();
  }

  private loadColors(): void {
    try {
      const colorsPath = path.join(this.extensionPath, 'src', 'colors.json');
      delete require.cache[require.resolve(colorsPath)];
      this.colors = require(colorsPath);
    } catch (error) {
      console.error('Failed to load colors.json:', error);
      throw new Error(`Failed to load colors.json: ${error}`);
    }
  }

  refresh(): void {
    this.loadColors();
    this._onDidChangeTreeData.fire();
  }

  getTreeItem(element: ThemeItem): vscode.TreeItem {
    const collapsibleState =
      element.type === 'category'
        ? vscode.TreeItemCollapsibleState.Collapsed
        : vscode.TreeItemCollapsibleState.None;
    return new ThemeTreeItem(element, collapsibleState);
  }

  getChildren(element?: ThemeItem): Thenable<ThemeItem[]> {
    if (!element) {
      // Root level - return categories
      const categories = Object.keys(this.colors).map((category) => ({
        type: 'category' as const,
        name: this.formatCategoryName(category),
        category: category,
      }));
      return Promise.resolve(categories);
    } else if (element.type === 'category' && element.category) {
      // Category level - return colors in this category
      const categoryColors = this.colors[element.category];
      if (!categoryColors) {
        return Promise.resolve([]);
      }
      const colors = Object.entries(categoryColors).map(([name, hex]) => ({
        type: 'color' as const,
        name: this.formatColorName(name),
        category: element.category,
        baseColor: hex,
      }));
      return Promise.resolve(colors);
    }
    return Promise.resolve([]);
  }

  private formatCategoryName(category: string): string {
    return category
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  private formatColorName(name: string): string {
    return name
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  getColorCustomizations(item: ThemeItem): Record<string, string> | null {
    if (item.type !== 'color' || !item.baseColor) {
      return null;
    }
    const brightColor = generateBrightVersion(item.baseColor, 25);
    return generateColorCustomizations(item.baseColor, brightColor);
  }
}
