export interface ServiceItem {
  name: string;
  port: number;
  forward_url: string;
  active: boolean;
  up: boolean;
}

export interface ServicesInfo {
  env?: string;
  services: ServiceItem[];
}

export interface SwitchServiceRequest {
  name: string;
  active: boolean;
}

export interface Traffic {
  id: number;
  service_name?: string;
  method: string;
  url: string;
  req_headers: {[key: string]: string;};
  req_body?: string;
  status_code: number;
  resp_headers: {[key: string]: string;};
  resp_body?: string;
  timestamp?: string;
  duration_ms?: number;
}

export interface TrafficsResponse {
  traffics: Traffic[];
}

export type GeneratorFormat =
  'CURL' | 'CURL_WINDOWS' | 'SPRING_BOOT_SERVER_MVC' | 'SPRINT_BOOT_SERVER_FLUX'|
  'SPRINT_BOOT_CLIENT_TEMPLATE' | 'OPENAPI_JAVA';

export interface GenerateRequest {
  trafficId: number,
  format: GeneratorFormat,
}


export interface GeneratedFile {
  file_name: string,
  content: string
}
export interface GenerateResponse {
  files: GeneratedFile[]
}
