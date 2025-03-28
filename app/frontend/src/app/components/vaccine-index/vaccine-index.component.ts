import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { DropdownModule } from 'primeng/dropdown';
import { TextInputComponent } from '../text/text-input/text-input.component';
import { Message, MessageRole } from '../../types/message.type';
import { TextSystemComponent } from '../text/text-system/text-system.component';
import { TextUserComponent } from '../text/text-user/text-user.component';
import { InputTextModule } from 'primeng/inputtext';
import { MessageService } from 'primeng/api';
import { EndpointService } from '../../services/endpoint.service';
import { Signup } from '../../types/signup.type';
import { Login } from '../../types/login.type';

@Component({
  selector: 'app-vaccine-index',
  standalone: true,
  imports: [
    CommonModule,
    ButtonModule,
    CardModule,
    FormsModule,
    DropdownModule,
    TextInputComponent,
    TextSystemComponent,
    TextUserComponent,
    InputTextModule,
    ReactiveFormsModule
  ],
  templateUrl: './vaccine-index.component.html',
  styleUrl: './vaccine-index.component.css'
})
export class VaccineIndexComponent {
  @ViewChild('scrollableTextContent') private scrollableTextContent!: ElementRef;

  user: string = MessageRole.User;
  system: string = MessageRole.Assistant;

  isSignUp = false;

  greeting: Message[] = [
    {
      role: MessageRole.Assistant,
      message:
        '<b>Welcome to the Beta version of HealthHub AI!</b><br><br>I am your friendly AI assistant, here to help you explore health information on HealthHub. You may ask questions in English, Chinese, Malay, or Tamil.<br><br>My responses may not always be perfect, as I am built on experimental technology and still learning progressively, but I will do my best to assist.<br><br>To ask a question, you can:<br>1. <b>Hold the voice button</b> (🎙️) to speak;<br>2. <b>Type</b> in your question (💬);<br>3. <b>Select from the suggested questions</b>.<br><br>How can I assist you today?<br><br>'
    }
  ];

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

  constructor(
    private toastService: MessageService,
    private endpointService: EndpointService
  ) {}

  loginForm: FormGroup = new FormGroup({
    username: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    password: new FormControl<string>('', [Validators.required, Validators.maxLength(15)])
  });

  signupForm: FormGroup = new FormGroup({
    nric: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    first_name: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    last_name: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    email: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    date_of_birth: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    gender: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    postal_code: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    password: new FormControl<string>('', [Validators.required, Validators.maxLength(15)]),
    cfm_password: new FormControl<string>('', [Validators.required, Validators.maxLength(15)])
  });

  toggleForm() {
    this.isSignUp = !this.isSignUp;
  }

  login() {
    if (this.loginForm.invalid) {
      this.loginForm.markAllAsTouched();
      this.toastService.add({
        severity: 'error',
        summary: 'Error!',
        detail: 'Wrong ID or password'
      });
      return;
    } else {
      const loginData: Login = {
        username: this.loginForm.value.username,
        password: this.loginForm.value.password
      };

      this.endpointService.login(loginData).subscribe({
        next: () => {
          this.toastService.add({
            severity: 'success',
            summary: 'Welcome!',
            detail: 'You have logged in'
          });
        },
        error: error => {
          this.toastService.add({
            severity: 'error',
            summary: 'Login Failed',
            detail: 'Wrong ID or password'
          });
        }
      });
    }
  }

  signup() {
    if (this.signupForm.invalid) {
      this.signupForm.markAllAsTouched();
      this.toastService.add({
        severity: 'error',
        summary: 'Error!',
        detail: 'An error occurred while creating your account'
      });
      return;
    } else {
      const signupData: Signup = {
        nric: this.signupForm.value.nric,
        first_name: this.signupForm.value.first_name,
        last_name: this.signupForm.value.last_name,
        email: this.signupForm.value.email,
        date_of_birth: this.signupForm.value.date_of_birth,
        gender: this.signupForm.value.gender,
        postal_code: this.signupForm.value.postal_code,
        password: this.signupForm.value.password,
        password_confirm: this.signupForm.value.cfm_password
      };

      const dummySignupData: Signup = {
        nric: this.generateRandomNRIC(),
        first_name: 'first_name',
        last_name: 'last_name',
        email: this.generateRandomEmail(),
        date_of_birth: '2025-03-27',
        gender: 'F',
        postal_code: '111111',
        password: '1',
        password_confirm: '1'
      };

      this.endpointService.signup(dummySignupData).subscribe({
        next: () => {
          this.toastService.add({
            severity: 'success',
            summary: 'Welcome!',
            detail: 'Account created successfully'
          });
          this.isSignUp = false;
        },
        error: error => {
          this.toastService.add({
            severity: 'error',
            summary: 'Signup Failed',
            detail: 'An error occurred while creating your account'
          });
        }
      });
    }
  }

  generateRandomNRIC = (): string => {
    const prefix = ['S', 'T', 'F', 'G'][Math.floor(Math.random() * 4)]; // Random prefix
    const digits = Math.floor(1000000 + Math.random() * 9000000).toString(); // Random 7-digit number
    const suffix = String.fromCharCode(65 + Math.floor(Math.random() * 26)); // Random letter (A-Z)
    return `${prefix}${digits}${suffix}`;
  };

  generateRandomEmail = (): string => {
    const timestamp = Date.now(); // Use timestamp for uniqueness
    return `user${timestamp}@example.com`;
  };
}
