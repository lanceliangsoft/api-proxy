import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { webSocket, WebSocketSubject } from "rxjs/webSocket";


@Injectable({
  providedIn: 'root'
})
export class EventService {
  private readonly WS_URL = 'ws://localhost:8000/ws/traffics';

  private socketSubject!: WebSocketSubject<string>;

  socket$!: Observable<string>;

  constructor() {
    this.connect();
  }

  public connect() {
    if (!this.socketSubject || this.socketSubject.closed) {
      this.socketSubject = webSocket({
        url: this.WS_URL,
        openObserver: {
          next: () => console.log('WebSocket connection established.'),
        },
        closeObserver: {
          next: () => console.log('WebSocket connection closed.'),
        }
      });
    }

    this.socket$ = this.socketSubject.asObservable();
  }

  public close(): void {
    if (this.socketSubject) {
      this.socketSubject.complete();
    }
  }
}
