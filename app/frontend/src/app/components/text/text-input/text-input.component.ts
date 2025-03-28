import { CommonModule } from '@angular/common';
import { Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Button } from 'primeng/button';
import { LucideAngularModule } from 'lucide-angular';
import { InputTextModule } from 'primeng/inputtext';

@Component({
  selector: 'app-text-input',
  standalone: true,
  imports: [LucideAngularModule, FormsModule, Button, CommonModule, ReactiveFormsModule, FormsModule, InputTextModule],
  templateUrl: './text-input.component.html',
  styleUrl: './text-input.component.css'
})
export class TextInputComponent {
  @Output() heightChange = new EventEmitter<number>();

  @ViewChild('inputTextarea') inputTextarea!: ElementRef<HTMLTextAreaElement>;
  @ViewChild('inputTextContainer') inputTextContainer!: ElementRef<HTMLTextAreaElement>;

  remainingChars: number = 1000;

  ngAfterViewInit(): void {
    this.emitHeightChange(); // Initial height emission
  }

  adjustTextareaRows(): void {
    const textarea = this.inputTextarea.nativeElement;
    if (textarea.value === '') {
      textarea.rows = 1;
    } else {
      textarea.rows = 1; // Reset to 1 row to recalculate the correct number of rows
      const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight, 10);
      const rows = Math.floor((textarea.scrollHeight - 15) / lineHeight);
      textarea.rows = rows < 3 ? rows : 3; // Set rows to the calculated value or maximum 3
      this.emitHeightChange();
    }
  }

  private emitHeightChange(): void {
    setTimeout(() => {
      const height = this.inputTextContainer.nativeElement.getBoundingClientRect().height;
      this.heightChange.emit(height);
    }, 0);
  }
}
