import { GeneratedFile } from "../services/model";

export interface GroupedValues<T> {
  title: string;
  values: T[];
}

export function groupBy<T>(list: T[], keyGetter: (item: T) => string): GroupedValues<T>[] {
  const map: { [key: string]: T[] } = {};
  list.forEach((item) => {
    const key = keyGetter(item);
    const collection = map[key];
    if (!collection) {
      map[key] = [item];
    } else {
      collection.push(item);
    }
  });
  return Object.entries(map).map(([title, values]) => ({ title, values }));
}

export function formatTimestamp(timestamp: string | undefined): string {
  if (!timestamp) {
    return '';
  }

  const date = new Date(timestamp);
  if (isNaN(date.getTime())) {
    return '';
  }

  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const year = date.getFullYear();

  return `${year}-${month}-${day} ${date.getHours()}:${date.getMinutes()}:${date.getSeconds()}`;
}

export function simplifyName(host: string): string {
  return host.replace(/^www\./, '').replace(/(\.com)(:\d+)$/, '');
}

export function isJson(str: string | null | undefined): boolean {
  return str !== null && str !== undefined
    && (str.startsWith('{') && str.endsWith('}')
      || (str.startsWith('[') && str.endsWith(']')));
}

export function formatJson(value: string, pretty: boolean): string {
  if (isJson(value as string)) {
    try {
      const obj = JSON.parse(value);
      if (pretty) {
        return JSON.stringify(obj, null, 2);
      } else {
        return JSON.stringify(obj);
      }
    } catch (err) {
      console.warn(err);
    }
  }
  return value;
}

export function mergeFiles(files: GeneratedFile[], comment_symbol: string): string {
    return files.map(file => `${comment_symbol} ${file.file_name}\n${file.content}\n`).join("\n");
}
