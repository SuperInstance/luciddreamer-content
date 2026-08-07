/**
 * Vessel App Registry
 *
 * The hermit crab's rooms. Each app is a compartment in the submarine.
 * Replaces OpenRoom's generic desktop apps with vessel-themed rooms.
 */

import * as idb from './diskStorage';

// ============ Type Definitions ============

export interface AppActionDef {
  name: string;
  description: string;
  params: Array<{
    name: string;
    type: string;
    description: string;
    required?: boolean;
    enum?: string[];
  }>;
}

export interface AppDef {
  appId: number;
  appName: string;
  route: string;
  displayName: string;
  actions: AppActionDef[];
}

// ============ Static App Registry ============

interface AppStaticDef {
  appId: number;
  appName: string;
  route: string;
  displayName: string;
  sourceDir?: string;
  icon?: string;
  color?: string;
  defaultSize?: { width: number; height: number };
}

const APP_STATIC_REGISTRY: AppStaticDef[] = [
  { appId: 1, appName: 'os', route: '/home', displayName: 'Vessel' },
  {
    appId: 20,
    appName: 'theTap',
    route: '/theTap',
    displayName: 'The Tap',
    sourceDir: 'TheTap',
    icon: 'Music',
    color: '#b87333',
    defaultSize: { width: 820, height: 640 },
  },
  {
    appId: 21,
    appName: 'theHold',
    route: '/theHold',
    displayName: 'The Hold',
    sourceDir: 'TheHold',
    icon: 'BookOpen',
    color: '#d4943a',
    defaultSize: { width: 900, height: 600 },
  },
  {
    appId: 22,
    appName: 'theChartRoom',
    route: '/theChartRoom',
    displayName: 'The Chart Room',
    sourceDir: 'TheChartRoom',
    icon: 'Compass',
    color: '#4a90a4',
    defaultSize: { width: 1000, height: 680 },
  },
  {
    appId: 23,
    appName: 'theEngineRoom',
    route: '/theEngineRoom',
    displayName: 'The Engine Room',
    sourceDir: 'TheEngineRoom',
    icon: 'Gauge',
    color: '#c4762d',
    defaultSize: { width: 700, height: 560 },
  },
  {
    appId: 24,
    appName: 'theBridge',
    route: '/theBridge',
    displayName: 'The Bridge',
    sourceDir: 'TheBridge',
    icon: 'Radio',
    color: '#a78bfa',
    defaultSize: { width: 600, height: 520 },
  },
  {
    appId: 25,
    appName: 'theLogbook',
    route: '/theLogbook',
    displayName: 'The Logbook',
    sourceDir: 'TheLogbook',
    icon: 'ScrollText',
    color: '#5a8a6a',
    defaultSize: { width: 800, height: 560 },
  },
  {
    appId: 26,
    appName: 'theCrowsNest',
    route: '/theCrowsNest',
    displayName: "The Crow's Nest",
    sourceDir: 'TheCrowsNest',
    icon: 'Search',
    color: '#7a9ab0',
    defaultSize: { width: 700, height: 560 },
  },
];

// OS actions
const OS_ACTIONS: AppActionDef[] = [
  {
    name: 'OPEN_APP',
    description: 'Open a specified app. Pass app_id as the application ID',
    params: [
      {
        name: 'app_id',
        type: 'string',
        description: `Application ID (${APP_STATIC_REGISTRY.filter((a) => a.appName !== 'os')
          .map((a) => `${a.appId}=${a.displayName}`)
          .join(', ')})`,
        required: true,
      },
    ],
  },
  {
    name: 'CLOSE_APP',
    description: 'Close a specified app. Pass app_id as the application ID',
    params: [{ name: 'app_id', type: 'string', description: 'Application ID', required: true }],
  },
  {
    name: 'SET_WALLPAPER',
    description:
      'Change the vessel wallpaper. wallpaper_url must be a https URL or a data URL (data:image/...).',
    params: [
      {
        name: 'wallpaper_url',
        type: 'string',
        description: 'https URL or data URL for the wallpaper',
        required: true,
      },
    ],
  },
];

// ============ Helper Query Functions ============

export function getAppDisplayName(appId: number): string {
  return APP_STATIC_REGISTRY.find((a) => a.appId === appId)?.displayName ?? `App ${appId}`;
}

export function getAppDefaultSize(appId: number): { width: number; height: number } {
  return (
    APP_STATIC_REGISTRY.find((a) => a.appId === appId)?.defaultSize ?? { width: 600, height: 400 }
  );
}

export function getDesktopApps(): Array<{
  appId: number;
  displayName: string;
  icon: string;
  color: string;
}> {
  return APP_STATIC_REGISTRY.filter((a) => a.appName !== 'os' && a.icon && a.color).map((a) => ({
    appId: a.appId,
    displayName: a.displayName,
    icon: a.icon!,
    color: a.color!,
  }));
}

export function getSourceDirToAppName(): Record<string, string> {
  const map: Record<string, string> = {};
  for (const app of APP_STATIC_REGISTRY) {
    if (app.sourceDir) map[app.sourceDir] = app.appName;
  }
  return map;
}

export function getSourceDirToAppId(): Record<string, number> {
  const map: Record<string, number> = {};
  for (const app of APP_STATIC_REGISTRY) {
    if (app.sourceDir) map[app.sourceDir] = app.appId;
  }
  return map;
}

// ============ Full Registry ============

export let APP_REGISTRY: AppDef[] = APP_STATIC_REGISTRY.map((app) => ({
  ...app,
  actions: app.appName === 'os' ? OS_ACTIONS : [],
}));

// ============ Meta.yaml Parsing (unchanged from OpenRoom) ============

function parseMetaYamlActions(yamlContent: string): AppActionDef[] {
  const actions: AppActionDef[] = [];
  if (/^actions:\s*\[\]\s*$/m.test(yamlContent)) return actions;
  const actionsMatch = yamlContent.match(/^actions:\s*$/m);
  if (!actionsMatch) return actions;
  const actionsStart = actionsMatch.index! + actionsMatch[0].length;
  const restContent = yamlContent.slice(actionsStart);
  const lines = restContent.split('\n');
  parseStandardActions(lines, actions);
  return actions;
}

function parseStandardActions(lines: string[], actions: AppActionDef[]): void {
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    if (line.match(/^\S/) && line.trim() !== '') break;
    const typeMatch = line.match(/^\s+-\s+type:\s+(\S+)/);
    if (typeMatch) {
      const action: AppActionDef = { name: typeMatch[1], description: '', params: [] };
      i++;
      while (i < lines.length) {
        const l = lines[i];
        if (l.match(/^\s+-\s+type:\s/) || (l.match(/^\S/) && l.trim() !== '')) break;
        const descMatch = l.match(/^\s+description:\s*>?\s*$/);
        if (descMatch) {
          i++;
          const descLines: string[] = [];
          while (i < lines.length && lines[i].match(/^\s{6,}/) && !lines[i].match(/^\s+\w+:/)) {
            descLines.push(lines[i].trim());
            i++;
          }
          action.description = descLines.join(' ');
          continue;
        }
        const descInlineMatch = l.match(/^\s+description:\s+(.+)$/);
        if (descInlineMatch) {
          action.description = descInlineMatch[1].trim();
          i++;
          continue;
        }
        const paramsMatch = l.match(/^\s+params:\s*$/);
        if (paramsMatch) {
          i++;
          parseParamsList(lines, i, action.params, (newI) => { i = newI; });
          continue;
        }
        if (l.match(/^\s+params:\s*\[\]\s*$/)) { i++; continue; }
        i++;
      }
      actions.push(action);
    } else {
      i++;
    }
  }
}

function parseParamsList(
  lines: string[],
  startI: number,
  params: AppActionDef['params'],
  setI: (i: number) => void,
): void {
  let i = startI;
  while (i < lines.length) {
    const l = lines[i];
    const paramNameMatch = l.match(/^\s+-\s+name:\s+(\S+)/);
    if (!paramNameMatch) break;
    const param: AppActionDef['params'][0] = {
      name: paramNameMatch[1],
      type: 'string',
      description: paramNameMatch[1],
    };
    i++;
    while (i < lines.length) {
      const pl = lines[i];
      if (pl.match(/^\s+-\s+name:\s/) || !pl.match(/^\s{8,}/)) break;
      const typeMatch = pl.match(/^\s+type:\s+(\S+)/);
      if (typeMatch) { param.type = typeMatch[1]; i++; continue; }
      const descMatch = pl.match(/^\s+description:\s+(.+)$/);
      if (descMatch) { param.description = descMatch[1].trim(); i++; continue; }
      const reqMatch = pl.match(/^\s+required:\s+(true|false)/);
      if (reqMatch) { param.required = reqMatch[1] === 'true'; i++; continue; }
      const enumMatch = pl.match(/^\s+enum:\s+\[(.+)\]/);
      if (enumMatch) { param.enum = enumMatch[1].split(',').map((s) => s.trim().replace(/['"]/g, '')); i++; continue; }
      i++;
    }
    params.push(param);
  }
  setI(i);
}

// ============ Dynamic Loading ============

let _loaded = false;

export async function loadActionsFromMeta(): Promise<void> {
  if (_loaded) return;
  const loaded: AppDef[] = [];
  for (const app of APP_STATIC_REGISTRY) {
    if (app.appName === 'os') {
      loaded.push({ ...app, actions: OS_ACTIONS });
      continue;
    }
    const metaPath = `apps/${app.appName}/meta.yaml`;
    try {
      const content = await idb.getFile(metaPath);
      if (content && typeof content === 'string') {
        const actions = parseMetaYamlActions(content);
        loaded.push({ ...app, actions });
      } else {
        loaded.push({ ...app, actions: [] });
      }
    } catch {
      loaded.push({ ...app, actions: [] });
    }
  }
  APP_REGISTRY = loaded;
  _loaded = true;
}

export function resetActionsCache(): void {
  _loaded = false;
}

// ============ Tool Definitions ============

export function getAppActionToolDefinition(): {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: { type: 'object'; properties: Record<string, unknown>; required: string[] };
  };
} {
  return {
    type: 'function',
    function: {
      name: 'app_action',
      description:
        "Trigger an action on a vessel app. Read the app's meta.yaml first to discover available action types and their parameters. " +
        'OS-level actions (OPEN_APP, CLOSE_APP, SET_WALLPAPER) MUST use app_name="os".',
      parameters: {
        type: 'object',
        properties: {
          app_name: {
            type: 'string',
            description: 'The appName of the target app (from list_apps)',
          },
          action_type: {
            type: 'string',
            description: 'The action type to trigger (e.g. PLAY_EPISODE, SEARCH_CORPUS, OPEN_APP)',
          },
          params: {
            type: 'string',
            description: 'JSON string of action parameters',
          },
        },
        required: ['app_name', 'action_type'],
      },
    },
  };
}

export function resolveAppAction(
  appName: string,
  actionType: string,
): { appId: number; actionType: string } | string {
  const app = APP_REGISTRY.find((a) => a.appName === appName);
  if (!app) return `error: unknown app "${appName}". Call list_apps to see available apps.`;
  return { appId: app.appId, actionType };
}

export function getListAppsToolDefinition(): {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: { type: 'object'; properties: Record<string, unknown>; required: string[] };
  };
} {
  return {
    type: 'function',
    function: {
      name: 'list_apps',
      description:
        'List all available apps on the vessel. Returns app names and display names. Call this first to discover what apps are available.',
      parameters: { type: 'object', properties: {}, required: [] },
    },
  };
}

export function executeListApps(): string {
  const apps = APP_REGISTRY.filter((a) => a.appName !== 'os').map(
    (a) => `${a.displayName} (appId: ${a.appId}, appName: ${a.appName})`,
  );
  return (
    `Available apps on the vessel:\n${apps.join('\n')}\n\n` +
    'OS-level actions (use app_name="os"):\n' +
    '- OPEN_APP: open an app (params: app_id)\n' +
    '- CLOSE_APP: close an app (params: app_id)\n' +
    '- SET_WALLPAPER: change wallpaper (params: wallpaper_url)'
  );
}
