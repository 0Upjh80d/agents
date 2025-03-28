import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VaccineIndexComponent } from './vaccine-index.component';

describe('VaccineIndexComponent', () => {
  let component: VaccineIndexComponent;
  let fixture: ComponentFixture<VaccineIndexComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VaccineIndexComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(VaccineIndexComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
