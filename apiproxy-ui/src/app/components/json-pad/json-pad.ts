import { Component, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { FormsModule } from '@angular/forms';
import { ConsoleService } from '../../services/service';
import { formatJson, mergeFiles } from '../../utils/utils';
import { MatSlideToggle } from "@angular/material/slide-toggle";
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
  selector: 'app-json-pad',
  imports: [MatButtonModule, MatTabsModule, FormsModule, MatSlideToggle, MatFormFieldModule, MatInputModule],
  templateUrl: './json-pad.html',
  styleUrl: './json-pad.scss',
})
export class JsonPad {
  private _consoleService = inject(ConsoleService);

  formatted = signal<boolean>(false);
  rootType = signal<string>("");
  json = signal<string>("");
  csCode = signal<string>("");
  javaCode = signal<string>("");
  tsCode = signal<string>("");

  async formattedChange() {
    this.formatted.update(checked => {
      this.json.update(value => formatJson(value, !checked));
      return !checked;
    })
  }

  async generate() {
    if (this.json() === '') {
      alert('Input JSON text');
      return;
    }
    if (this.rootType() === '') {
      alert('Input a Root Type');
      return;
    }
    const csResp = await this._consoleService.generateModel(this.json(), "CS", this.rootType());
    this.csCode.set(mergeFiles(csResp.files, "//"));

    const javaResp = await this._consoleService.generateModel(this.json(), "JAVA", this.rootType());
    this.javaCode.set(mergeFiles(javaResp.files, "//"));

    const tsResp = await this._consoleService.generateModel(this.json(), "TYPESCRIPT", this.rootType());
    this.tsCode.set(mergeFiles(tsResp.files, "//"));
  }
}
