import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TrafficDetail } from './traffic-detail';

describe('TrafficDetail', () => {
  let component: TrafficDetail;
  let fixture: ComponentFixture<TrafficDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TrafficDetail],
    }).compileComponents();

    fixture = TestBed.createComponent(TrafficDetail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
