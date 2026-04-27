import { Component, computed, input, signal } from '@angular/core';
import { Traffic } from '../../services/model';
import { MatTableModule } from '@angular/material/table';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { Generator } from "../generator/generator";
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormsModule } from '@angular/forms';
import { FormatJsonPipe } from '../../derivatives/format-json-pipe';

const MAX_HEADERS = 6;

@Component({
  selector: 'app-traffic-detail',
  imports: [
    CommonModule, MatTableModule, MatTabsModule, MatSlideToggleModule, Generator,
    FormsModule, MatSlideToggleModule,
    FormatJsonPipe
],
  templateUrl: './traffic-detail.html',
  styleUrl: './traffic-detail.scss',
  providers: [FormatJsonPipe]
})
export class TrafficDetail {

  displayedColumns: string[] = ['name', 'value'];
  traffic = input<Traffic|undefined>(undefined);
  reqHeaders = computed(() =>
    Object.entries(this.traffic()?.req_headers ?? {})
      .map(([name, value]) => ({name, value}))
    );

  respHeaders = computed(() =>
    Object.entries(this.traffic()?.resp_headers ?? {})
      .map(([name, value]) => ({name, value}))
    );
  formatReq = signal<boolean>(false);
  formatResp = signal<boolean>(false);
}
