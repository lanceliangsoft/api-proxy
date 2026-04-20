import { Component, input, signal, effect, computed, inject, OnInit, EventEmitter, Output } from '@angular/core';
import { ServiceItem } from '../../services/model';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { form, FormField } from '@angular/forms/signals';
import { ConsoleService } from '../../services/service';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { getUrlFromHost } from '../../utils/restUtil';

@Component({
  selector: 'app-service-detail',
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatSlideToggleModule, MatButtonModule],
  templateUrl: './service-detail.html',
  styleUrl: './service-detail.scss',
})
export class ServiceDetail implements OnInit {
  private _consoleService = inject(ConsoleService);

  @Output() serviceAdded = new EventEmitter<ServiceItem>(true);
  service = input<ServiceItem | undefined>(undefined);
  newServiceHost = input<string>('');
  editMode = computed(() => this.service() !== undefined);

  // signal Form is buggy, use reactive form instead.
  serviceForm = new FormGroup({
    name: new FormControl(''),
    port: new FormControl(''),
    forward_url: new FormControl(''),
    active: new FormControl(false),
  })

  constructor() {
    const self = this;
    effect(async () => await self.reset());
  }

  async ngOnInit() {
    await this.reset();
  }

  async save() {
      const formValue = this.serviceForm.value;
      const service: ServiceItem = {
        name: formValue.name || this.newServiceHost() || '',
        port: formValue.port ? parseInt(formValue.port, 10) : await this._consoleService.getNextAvailablePort(8000),
        forward_url: formValue.forward_url || '',
        active: formValue.active || false,
        up: false
      }
    const prevService = this.service();
    if (prevService) {
      // Update existing service

      service.name = prevService.name; // name is not editable.
      const updatedService = await this._consoleService.updateService(service);
      if (updatedService) {
        Object.assign(prevService, updatedService);
      }
    } else {
      // Create new service

      console.log('Creating new service:', JSON.stringify(service));
      const createdService = await this._consoleService.addService(service);
      if (createdService) {
        console.log('New service created:', JSON.stringify(createdService));
        this.serviceAdded.emit(createdService);
      }
    }
  }

  async reset() {
    const service = this.service();
    if (service) {
      this.serviceForm.setValue({
        name: service.name ?? '',
        port: '' + service.port,
        forward_url: service.forward_url ?? '',
        active: service.active ?? false,
      });
    } else {
      this.serviceForm.setValue({
        name: this.newServiceHost() || '',
        port: '' + await this._consoleService.getNextAvailablePort(8000),
        forward_url: getUrlFromHost(this.newServiceHost()),
        active: false
      });
      console.log('Resetting form for new service: ', JSON.stringify(this.serviceForm.value));
    }
  }
}
