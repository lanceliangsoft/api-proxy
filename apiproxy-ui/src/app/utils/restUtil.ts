import { Traffic } from "../services/model";

export function hostOfUrl(url: string): string {
  try {
    if (!url) {
      return '';
    }
    const urlObj = new URL(url);
    return urlObj.host + ':' + (urlObj.port || (urlObj.protocol === 'https:' ? '443' : '80'));
  } catch (e) {
    console.error(`Invalid URL: ${url}`);
    return '??';
  }
}

export function urlMatches(url: string, host: string): boolean {
    const urlHost = hostOfUrl(url);
    return urlHost === host;
}

export function getUrlFromHost(host: string): string {
    const parts = host.split(':');
    const port = parts[1];
    if (port === '80') {
        return `http://${parts[0]}`;
    } else if (port === '443') {
        return `https://${parts[0]}`;
    } else {
      return `https://${host}`;
    }
}
