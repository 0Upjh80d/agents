import { Component, OnInit, EventEmitter, Output, ViewChild, ElementRef } from '@angular/core';
import { DialogModule } from 'primeng/dialog';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-disclaimer',
  standalone: true,
  imports: [CommonModule, DialogModule],
  templateUrl: './disclaimer.component.html',
  styleUrls: ['./disclaimer.component.css']
})
export class DisclaimerComponent implements OnInit {
  @Output() disclaimerClosed = new EventEmitter<void>();
  isDisclaimerVisible: boolean = false;
  headerDisclaimer: string;
  translatedHtml: string = '';

  @ViewChild('disclaimerContent') disclaimerContent!: ElementRef;

  constructor() {
    this.headerDisclaimer = '';
  }

  ngOnInit(): void {
    this.checkDisclaimerStatus();
  }

  checkDisclaimerStatus() {
    const readDisclaimer = sessionStorage.getItem('readDisclaimer');

    if (!readDisclaimer) {
      this.showDisclaimer();
    }
  }

  showDisclaimer() {
    this.isDisclaimerVisible = true;
  }

  closeDisclaimer() {
    this.isDisclaimerVisible = false;
    sessionStorage.setItem('readDisclaimer', 'true');
  }

  getTranslatedText(): string {
    let translatedText = 'important notice';
    ('To begin, please click I Agree to Proceed to accept our Website Terms of Use and Website Privacy Policy.'); // Default to empty string if undefined

    return translatedText;
  }
  loadTranslatedText(): void {
    // Ensure languageService is available

    let translatedText = 'important noticeTo begin, please click I Agree to Proceed to accept our Website Terms of Use and Website Privacy Policy';

    this.translatedHtml = translatedText; // Update the component variable
  }
}
