import { ComponentFixture, TestBed } from '@angular/core/testing';

import { JsonPad } from './json-pad';

describe('JsonPad', () => {
  let component: JsonPad;
  let fixture: ComponentFixture<JsonPad>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [JsonPad],
    }).compileComponents();

    fixture = TestBed.createComponent(JsonPad);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
