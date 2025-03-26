import { ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { DropdownModule } from 'primeng/dropdown';
import { TextInputComponent } from '../text/text-input/text-input.component';
import { Message, MessageRole } from '../../types/message.type';
import { TextSystemComponent } from '../text/text-system/text-system.component';
import { TextUserComponent } from '../text/text-user/text-user.component';

@Component({
  selector: 'app-vaccine-index',
  standalone: true,
  imports: [ButtonModule, CardModule, FormsModule, DropdownModule, TextInputComponent, TextSystemComponent, TextUserComponent],
  templateUrl: './vaccine-index.component.html',
  styleUrl: './vaccine-index.component.css'
})
export class VaccineIndexComponent {
  @ViewChild('scrollableTextContent') private scrollableTextContent!: ElementRef;

  user: string = MessageRole.User;
  system: string = MessageRole.Assistant;

  greeting: Message[] = [{
      role: MessageRole.Assistant,
      message:  '<b>Welcome to the Beta version of HealthHub AI!</b><br><br>I am your friendly AI assistant, here to help you explore health information on HealthHub. You may ask questions in English, Chinese, Malay, or Tamil.<br><br>My responses may not always be perfect, as I am built on experimental technology and still learning progressively, but I will do my best to assist.<br><br>To ask a question, you can:<br>1. <b>Hold the voice button</b> (🎙️) to speak;<br>2. <b>Type</b> in your question (💬);<br>3. <b>Select from the suggested questions</b>.<br><br>How can I assist you today?<br><br>'
    } ];
  
  messages: Message[] = [
    {
      role: MessageRole.User,
      message: 'Hi, I want to know about the COVID-19 vaccine.'
    },
    {
      role: MessageRole.Assistant,
      message:
        'Sure! The COVID-19 vaccine helps protect you from the virus that causes COVID-19. Would you like to know about the different types of vaccines available?'
    },
    {
      role: MessageRole.User,
      message: 'Yes, please tell me more about them.'
    },
    {
      role: MessageRole.Assistant,
      message:
        "There are several types of COVID-19 vaccines, including mRNA vaccines like Pfizer-BioNTech and Moderna, and vector vaccines like Johnson & Johnson's Janssen vaccine. Each has its own efficacy rates and dosing schedules.There are several types of COVID-19 vaccines, including mRNA vaccines like Pfizer-BioNTech and Moderna, and vector vaccines like Johnson & Johnson's Janssen vaccine. Each has its own efficacy rates and dosing schedules.There are several types of COVID-19 vaccines, including mRNA vaccines like Pfizer-BioNTech and Moderna, and vector vaccines like Johnson & Johnson's Janssen vaccine. Each has its own efficacy rates and dosing schedules.There are several types of COVID-19 vaccines, including mRNA vaccines like Pfizer-BioNTech and Moderna, and vector vaccines like Johnson & Johnson's Janssen vaccine. Each has its own efficacy rates and dosing schedules."
    },
    {
      role: MessageRole.User,
      message: 'How many doses do I need?'
    },
    {
      role: MessageRole.Assistant,
      message: 'Most mRNA vaccines require two doses, typically administered 3 to 4 weeks apart. The Johnson & Johnson vaccine requires only one dose.'
    },
    {
      role: MessageRole.User,
      message: 'What are the side effects?'
    },
    {
      role: MessageRole.Assistant,
      message:
        'Common side effects include soreness at the injection site, fatigue, headache, muscle pain, chills, fever, and nausea. These usually go away within a few days.'
    },
    {
      role: MessageRole.User,
      message: 'Is it safe for children?'
    },
    {
      role: MessageRole.Assistant,
      message: "Yes, the vaccines are safe for children aged 5 and older. It's important to consult with a healthcare provider for specific recommendations."
    },
    {
      role: MessageRole.User,
      message: 'Where can I get vaccinated?'
    },
    {
      role: MessageRole.Assistant,
      message:
        'You can get vaccinated at local health departments, pharmacies, and clinics. You can also visit the official health department website to find vaccination sites near you.'
    },
    {
      role: MessageRole.User,
      message: 'Thank you for the information!'
    },
    {
      role: MessageRole.Assistant,
      message: "You're welcome! If you have any more questions, feel free to ask."
    }
  ];
}
