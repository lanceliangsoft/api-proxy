import { Component, computed, input, signal } from '@angular/core';
import { Traffic } from '../../services/model';
import { MatTableModule } from '@angular/material/table';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { Generator } from "../generator/generator";
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

const MAX_HEADERS = 6;

@Component({
  selector: 'app-traffic-detail',
  imports: [CommonModule, MatTableModule, MatTabsModule, MatSlideToggleModule, Generator],
  templateUrl: './traffic-detail.html',
  styleUrl: './traffic-detail.scss',
})
export class TrafficDetail {

  displayedColumns: string[] = ['name', 'value'];
  traffic = input<Traffic|undefined>(undefined);
  reqHeadersAll = signal<boolean>(false);
  reqHeaders = computed(() =>
    Object.entries(this.traffic()?.req_headers ?? {})
      .map(([name, value]) => ({name, value}))
      .filter((value,index) => this.reqHeadersAll() || index < MAX_HEADERS)
    );

  respHeadersAll = signal<boolean>(false);
  respHeaders = computed(() =>
    Object.entries(this.traffic()?.resp_headers ?? {})
      .map(([name, value]) => ({name, value}))
      .filter((value,index) => this.respHeadersAll() || index < MAX_HEADERS)
    );

}
