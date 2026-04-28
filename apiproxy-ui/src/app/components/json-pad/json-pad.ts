import { Component, inject, signal } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatTabsModule } from '@angular/material/tabs';
import { FormsModule } from '@angular/forms';
import { ConsoleService } from '../../services/service';
import { formatJson, mergeFiles } from '../../utils/utils';

@Component({
  selector: 'app-json-pad',
  imports: [MatButtonModule, MatTabsModule, FormsModule],
  templateUrl: './json-pad.html',
  styleUrl: './json-pad.scss',
})
export class JsonPad {
  private _consoleService = inject(ConsoleService);

  json = signal<string>("");
  csCode = signal<string>("");
  javaCode = signal<string>("");
  tsCode = signal<string>("");

  async format() {
    this.json.update(value => formatJson(value, true));
  }

  async compact() {
    this.json.update(value => formatJson(value, false));
  }

  async generate() {
    const csResp = await this._consoleService.generateModel(this.json(), "CS", "RootEntity");
    this.csCode.set(mergeFiles(csResp.files, "//"));

    const javaResp = await this._consoleService.generateModel(this.json(), "JAVA", "RootEntity");
    this.javaCode.set(mergeFiles(javaResp.files, "//"));

    const tsResp = await this._consoleService.generateModel(this.json(), "TYPESCRIPT", "RootEntity");
    this.tsCode.set(mergeFiles(tsResp.files, "//"));
  }
}
