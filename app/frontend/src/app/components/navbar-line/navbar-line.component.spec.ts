import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NavbarLineComponent } from './navbar-line.component';

describe('NavbarLineComponent', () => {
  let component: NavbarLineComponent;
  let fixture: ComponentFixture<NavbarLineComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NavbarLineComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NavbarLineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
