import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { Message } from '../../../types/message.type';
import { MarkdownComponent } from '../../markdown/markdown.component';

@Component({
  selector: 'app-text-system',
  standalone: true,
  imports: [CommonModule, MarkdownComponent],
  templateUrl: './text-system.component.html',
  styleUrl: './text-system.component.css'
})
export class TextSystemComponent {
  @Input() message!: Message;
}
