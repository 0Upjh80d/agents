import { Component, Input } from '@angular/core';
import { Message } from '../../../types/message.type';

@Component({
  selector: 'app-text-user',
  standalone: true,
  imports: [],
  templateUrl: './text-user.component.html',
  styleUrl: './text-user.component.css'
})
export class TextUserComponent {
  @Input() message!: Message;
}
