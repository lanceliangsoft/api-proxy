import { Component, computed, input } from '@angular/core';
import { Traffic } from '../../services/model';
import { MatTableModule } from '@angular/material/table';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { Generator } from "../generator/generator";
import { MatSlideToggleModule } from '@angular/material/slide-toggle';

@Component({
  selector: 'app-traffic-detail',
  imports: [CommonModule, MatTableModule, MatTabsModule, MatSlideToggleModule, Generator],
  templateUrl: './traffic-detail.html',
  styleUrl: './traffic-detail.scss',
})
export class TrafficDetail {
  displayedColumns: string[] = ['name', 'value'];
  traffic = input<Traffic|undefined>(undefined);
  req_headers = computed(() =>
    Object.entries(this.traffic()?.req_headers ?? {})
      .map(([name, value]) => ({name, value})));

  resp_headers = computed(() =>
    Object.entries(this.traffic()?.resp_headers ?? {})
      .map(([name, value]) => ({name, value})));

}
