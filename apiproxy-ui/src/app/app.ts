import { Component, inject, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ConsoleService } from './services/service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  private _service = inject(ConsoleService);
  env = this._service.env;

}
