import { Component, EventEmitter, input, Output } from '@angular/core';
import { GroupedValues } from '../../utils/utils';
import { Traffic } from '../../services/model';
import { MatButtonModule } from '@angular/material/button';

@Component({
  selector: 'app-unmapped-group',
  imports: [MatButtonModule],
  templateUrl: './unmapped-group.html',
  styleUrl: './unmapped-group.scss',
})
export class UnmappedGroup {
  group = input<GroupedValues<Traffic> | undefined>(undefined);
  @Output() addService = new EventEmitter<string>(true);

  async addMappedService() {
    if (this.group()) {
      console.log('emitting addService event:', this.group()!.title);
      this.addService.emit(this.group()!.title);
      console.log('emitted addService event');
    }
  }
}
