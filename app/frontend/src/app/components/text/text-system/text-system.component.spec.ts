import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextSystemComponent } from './text-system.component';

describe('TextSystemComponent', () => {
  let component: TextSystemComponent;
  let fixture: ComponentFixture<TextSystemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextSystemComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextSystemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
