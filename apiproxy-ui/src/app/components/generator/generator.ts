import { Component, inject, input, signal } from '@angular/core';
import { GeneratorFormat, Traffic } from '../../services/model';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatButtonModule } from '@angular/material/button';
import { FormsModule } from '@angular/forms';
import { form, FormField } from '@angular/forms/signals';
import { ConsoleService } from '../../services/service';

interface GeneratingOptions {
  format: GeneratorFormat;
}

@Component({
  selector: 'app-generator',
  imports: [FormsModule, MatButtonModule, MatFormFieldModule, MatInputModule, MatSelectModule],
  templateUrl: './generator.html',
  styleUrl: './generator.scss',
})
export class Generator {
  private _consoleService = inject(ConsoleService);
  formats = ['CURL', 'CURL_WINDOWS', 'SPRING_BOOT_SERVER_WEB_MVC', 'SPRINT_BOOT_SERVER_WEB_FLUX',
    'SPRINT_BOOT_CLIENT_TEMPLATE', 'OPENAPI_JAVA'];
  traffic = input<Traffic | undefined>();
  format = signal<GeneratorFormat>('CURL');

  code = signal<string>("");


  async generate() {
    const traffic = this.traffic();
    if (!traffic) {
      return;
    }
    const response = await this._consoleService.generate(traffic.id, this.format());

    let comment_symbol: string;
    switch (this.format()) {
      case 'CURL':
        comment_symbol = '#';
        break;
      case 'CURL_WINDOWS':
        comment_symbol = 'rem';
        break;
      default:
        comment_symbol = '//';
    }
    this.code.set(response.files.map(file => `${comment_symbol} ${file.file_name}\n${file.content}\n`).join("\n"));
  }

  copy(inputElement: any) {
    inputElement.select();
    document.execCommand('copy');
    inputElement.setSelectionRange(0, 0);
  }
}
