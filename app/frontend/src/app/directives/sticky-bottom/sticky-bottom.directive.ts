import { AfterContentInit, AfterViewChecked, Directive, ElementRef } from '@angular/core';

@Directive({
  selector: '[appStickyBottom]',
  standalone: true
})
export class StickyBottomDirective implements AfterContentInit, AfterViewChecked {
  private supposedToBeStuck: boolean = false;
  private lastScrollPosition: number = 0;
  private userHasScrolled: boolean = false;

  constructor(private el: ElementRef) {
    this.el.nativeElement.addEventListener('scroll', () => {
      this.userHasScrolled = true;
      // scroll up && full height - top-overflow height - visible height  <= 2
      // supposedToBeStuck = element is scrolled to the bottom after the user has scrolled
      this.supposedToBeStuck =
        this.lastScrollPosition < this.el.nativeElement.scrollTop &&
        this.el.nativeElement.scrollHeight - this.el.nativeElement.clientHeight - this.el.nativeElement.scrollTop <= 2;
      this.lastScrollPosition = this.el.nativeElement.scrollTop;
    });
  }

  ngAfterContentInit() {
    this.scrollToBottom();
  }

  ngAfterViewChecked() {
    if (this.supposedToBeStuck || !this.userHasScrolled) {
      this.scrollToBottom();
    }
  }

  private scrollToBottom() {
    this.el.nativeElement.scrollTop = this.el.nativeElement.scrollHeight;
  }
}
