import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UnmappedGroup } from './unmapped-group';

describe('UnmappedGroup', () => {
  let component: UnmappedGroup;
  let fixture: ComponentFixture<UnmappedGroup>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UnmappedGroup],
    }).compileComponents();

    fixture = TestBed.createComponent(UnmappedGroup);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
