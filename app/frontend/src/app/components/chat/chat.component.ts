import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { TextInputComponent } from '../text-input/text-input.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, TextInputComponent],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.css'
})
export class ChatComponent {
  messages = [
    { role: 'user', text: 'Hello, how are you?' },
    { role: 'system', text: 'I am doing well, thank you!' },
    { role: 'user', text: 'What can you help me with?' }
  ];
  newMessage: string = '';
}
