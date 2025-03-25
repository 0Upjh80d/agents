import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TextUserComponent } from './text-user.component';

describe('TextUserComponent', () => {
  let component: TextUserComponent;
  let fixture: ComponentFixture<TextUserComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TextUserComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TextUserComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
