import { Component, computed, effect, inject, OnInit, signal } from '@angular/core';
import { MatListModule, MatListOption } from '@angular/material/list';
import { ConsoleService } from '../../services/service';
import { ServiceItem, ServicesInfo, Traffic } from '../../services/model';
import { MatButtonModule } from '@angular/material/button';
import { TrafficDetail } from '../traffic-detail/traffic-detail';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatTreeModule } from '@angular/material/tree';
import { groupBy, GroupedValues, formatTimestamp } from '../../utils/utils';
import { hostOfUrl, urlMatches } from '../../utils/restUtil';
import { MatIconModule } from '@angular/material/icon';
import { ServiceDetail } from '../service-detail/service-detail';
import { UnmappedGroup } from '../unmapped-group/unmapped-group';
import { MatFormField, MatInputModule } from "@angular/material/input";
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatTimepickerModule } from '@angular/material/timepicker';
import { FormsModule } from '@angular/forms';


export type DetailViewName = 'traffic' | 'service' | 'unmapped-group';

@Component({
  selector: 'app-dashboard',
  imports: [MatListModule, MatButtonModule, MatTreeModule, MatIconModule, MatSlideToggleModule,
    FormsModule, MatFormFieldModule, MatInputModule, MatDatepickerModule, MatTimepickerModule,
    TrafficDetail, ServiceDetail, UnmappedGroup, MatFormField],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard implements OnInit {
  private _consoleService = inject(ConsoleService);
  services = signal<ServiceItem[]>([]);
  traffics = signal<Traffic[]>([]);
  selectedService = signal<ServiceItem | undefined>(undefined);
  selectedTraffic = signal<Traffic | undefined>(undefined);
  selectedGroup = signal<GroupedValues<Traffic> | undefined>(undefined);
  newServiceHost = signal<string>('');
  detailView = signal<DetailViewName>('traffic');
  showAll = signal<boolean>(true);
  beginTime = signal<Date | undefined>(undefined);
  endTime = signal<Date | undefined>(undefined);
  trafficGroups = //signal<TrafficGroup[]>([{ title: 'any', traffics: [] }]);
    computed(() => groupBy<Traffic>(this.traffics(), (traffic) => hostOfUrl(traffic.url)));

  constructor() {
    effect(() => {

    });
  }

  childrenAccessor = (node: GroupedValues<Traffic> | Traffic) => {
    if ('values' in node) {
      return node.values;
    } else {
      return [];
    }
  }

  hasChild = (_: number, node: GroupedValues<Traffic> | Traffic) => {
    return 'values' in node && node.values.length > 0;
  }

  ngOnInit(): void {
    this.refresh();
  }

  addService() {
    this.selectedService.set(undefined);
    this.detailView.set('service');
  }

  async onServiceSelected(serviceName: string) {
    const service = this.services().find(s => s.name === serviceName);
    this.selectedService.set(service);
    this.detailView.set('service');

    await this.refreshTraffics();
  }

  async onTrafficSelected(traffic: GroupedValues<Traffic> | Traffic) {
    console.log('Traffic selected:', JSON.stringify(traffic));
    if ('title' in traffic) {
      const group = traffic as GroupedValues<Traffic>;
      const host = group.title as string;
      const serviceItem = this.services().find(s => urlMatches(s.forward_url, host));
      if (serviceItem) {
        this.selectedService.set(serviceItem);
        this.detailView.set('service');
      } else {
        console.warn(`No service found matching host: ${host}`);
        this.selectedGroup.set(group);
        this.detailView.set('unmapped-group');
      }
    } else {
      this.selectedTraffic.set(traffic as Traffic);
      this.detailView.set('traffic');
    }
  }

  async onToggleService(serviceName: string, previouslyChecked: boolean) {
    const active = !previouslyChecked;
    console.log(`onToggleService ${serviceName} active: ${active}`)
    const updatedItem = await this._consoleService.switchService(serviceName, active);

    this.services.update((items: ServiceItem[]) =>
      items.map(item => {
        if (updatedItem.name === item.name) {
          return updatedItem;
        } else {
          return item;
        }
      })
    );
  }

  private async refreshTraffics() {
    const trafficsInfo = await this._consoleService.retrieveTraffics(
      this.selectedService()?.name || 'http-proxy',
      this.beginTime(), this.endTime()
    );
    this.traffics.set(trafficsInfo.traffics);
  }

  async refresh(): Promise<void> {
    const servicesInfo = await this._consoleService.getServices();
    this.services.set(servicesInfo.services);

    await this.refreshTraffics();
  }

  getTrafficTime(traffic: Traffic): string {
    return formatTimestamp(traffic.timestamp);
  }

  getTrafficLabel(traffic: Traffic): string {
    return `${traffic.method} ${traffic.url}`;
  }

  onAddService() {
    console.log('onAddService()');
    const host = this.selectedGroup()?.title;
    if (host) {
      this.selectedService.set(undefined);
      this.newServiceHost.set(host);
      this.detailView.set('service');
    }
  }

  onServiceAdded(service: ServiceItem) {
    console.log('onServiceAdded:', JSON.stringify(service));
    this.services.update(services => [...services, service]);
  }

  onServiceDeleted(serviceName: string) {
    console.log('onServiceDeleted:', serviceName);
    this.services.update(services => services.filter(s => s.name !== serviceName));
    this.selectedService.set(undefined);
    this.detailView.set('traffic');
  }
}
