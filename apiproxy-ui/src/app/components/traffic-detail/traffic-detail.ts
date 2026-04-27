import { Component, computed, EventEmitter, inject, input, Output, signal } from '@angular/core';
import { Traffic } from '../../services/model';
import { MatTableModule } from '@angular/material/table';
import { CommonModule } from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { Generator } from "../generator/generator";
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { FormsModule } from '@angular/forms';
import { FormatJsonPipe } from '../../derivatives/format-json-pipe';
import { ConsoleService } from '../../services/service';
import { MatButtonModule } from '@angular/material/button';

const MAX_HEADERS = 6;

@Component({
  selector: 'app-traffic-detail',
  imports: [
    CommonModule, MatTableModule, MatTabsModule, MatSlideToggleModule, Generator,
    FormsModule, MatSlideToggleModule, MatButtonModule,
    FormatJsonPipe
],
  templateUrl: './traffic-detail.html',
  styleUrl: './traffic-detail.scss',
  providers: [FormatJsonPipe]
})
export class TrafficDetail {
  private _consoleService = inject(ConsoleService);
  @Output() trafficDeleted = new EventEmitter<number>();

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

  async deleteTraffic(id: number | undefined): Promise<void> {
    if (id && confirm(`Do you want to delete traffic ${id} - ${this.traffic()?.method} ${this.traffic()?.url}?`)) {
      const deleted = await this._consoleService.deleteTraffic(id);
      if (deleted) {
        this.trafficDeleted.emit(id);
      } else {
        alert(`failed to delete traffic ${id}`);
      }
    }
  }
}
