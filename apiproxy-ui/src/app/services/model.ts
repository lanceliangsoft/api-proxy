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
  'CURL' | 'CURL_WINDOWS' | 'SPRING_BOOT_WEB_MVC' | 'SPRING_BOOT_WEB_FLUX'|
  'ASP_NET_API' | 'GO_FIBER_API' | 'RUST_ACTIX_API' |
  'DOT_NET_CLIENT' | 'TYPESCRIPT_CLIENT' |
  'JAVA_CLIENT_JDK_HTTP' | 'JAVA_CLIENT_APACHE_HTTP' | 'JAVA_CLIENT_REST_TEMPLATE' | 'JAVA_CLIENT_WEB_FLUX';


export const GENERATOR_FORMATS :GeneratorFormat[] = [
  'CURL', 'CURL_WINDOWS', 'SPRING_BOOT_WEB_MVC', 'SPRING_BOOT_WEB_FLUX',
  'ASP_NET_API', 'GO_FIBER_API', 'RUST_ACTIX_API',
  'DOT_NET_CLIENT', 'TYPESCRIPT_CLIENT',
  'JAVA_CLIENT_JDK_HTTP', 'JAVA_CLIENT_APACHE_HTTP', 'JAVA_CLIENT_REST_TEMPLATE', 'JAVA_CLIENT_WEB_FLUX'
]

export type ModelFormat =
  'CS' | 'JAVA' | 'TYPESCRIPT' | 'PYTHON' | 'GO';

export interface GenerateRequest {
  traffic_id: number,
  format: GeneratorFormat,
}

export interface GenerateModelRequest {
  json_payload: string,
  format: ModelFormat,
  root_element: string,
}

export interface GeneratedFile {
  file_name: string,
  content: string,
}

export interface GenerateResponse {
  files: GeneratedFile[]
}
