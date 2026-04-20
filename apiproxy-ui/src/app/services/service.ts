import { Injectable, signal } from "@angular/core";
import { GenerateRequest, GenerateResponse, GeneratorFormat, ServiceItem, ServicesInfo, TrafficsResponse } from "./model";

@Injectable({
  providedIn: 'root'
})
export class ConsoleService {
  baseUrl = 'http://localhost:8000';
  env = signal('dev');

  async getServices(): Promise<ServicesInfo> {
    const response = await fetch(`${this.baseUrl}/api/services`);
    const data = await response.json();
    return data;
  }

  async addService(service: ServiceItem): Promise<ServiceItem> {
    const response = await fetch(`${this.baseUrl}/api/services`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(service)
    });
    const data = await response.json();
    return data;
  }

  async updateService(service: ServiceItem): Promise<ServiceItem> {
    const response = await fetch(`${this.baseUrl}/api/services`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(service)
    });
    const data = await response.json();
    return data;
  }

  async switchService(serviceName: string, active: boolean): Promise<ServiceItem> {
    const response = await fetch(
      `${this.baseUrl}/api/services/switch`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          name: serviceName,
          active
        })
      });
    return await response.json();
  }

  async retrieveTraffics(serviceName: string): Promise<TrafficsResponse> {
    const response = await fetch(`${this.baseUrl}/api/traffics/${serviceName}`);
    const data = await response.json();
    return data;
  }

  async getNextAvailablePort(startPort: number): Promise<number> {
    const response = await fetch(`${this.baseUrl}/api/next-port?start=${startPort}`);
    const data = await response.json();
    return data.port;
  }

  async generate(trafficId: number, format: GeneratorFormat): Promise<GenerateResponse> {
    console.log(`generate ${trafficId}, ${format}`)
    const response = await fetch(`${this.baseUrl}/api/generate`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          trafficId,
          format: format
        } as GenerateRequest)
      });
    const data = await response.json();
    return data;
  }
}
