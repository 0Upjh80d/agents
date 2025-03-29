import { CommonModule } from '@angular/common';
import { Component, ElementRef, ViewChild } from '@angular/core';
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
  isSinpassLogin = false;
  isLoggedIn = false;

  greeting: Message[] = [
    {
      role: MessageRole.Assistant,
      message:
        '<b>Welcome to the Beta version of HealthHub AI!</b><br><br>I am your friendly AI assistant, here to help you explore health information on HealthHub. You may ask questions in English, Chinese, Malay, or Tamil.<br><br>My responses may not always be perfect, as I am built on experimental technology and still learning progressively, but I will do my best to assist.<br><br>To ask a question, you can:<br>1. <b>Hold the voice button</b> (🎙️) to speak;<br>2. <b>Type</b> in your question (💬);<br>3. <b>Select from the suggested questions</b>.<br><br>How can I assist you today?<br><br>'
    }
  ];

  suggestedQns: String[] = ['Can you help me book my Vaccination?', 'Please show me my Vaccination history'];
  messages: Message[] = [];
  vaccinations: String[] = [];
  constructor(private toastService: MessageService, private endpointService: EndpointService) {}

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
          this.isSinpassLogin = false;
          this.isLoggedIn = true;

          this.endpointService.dummyRecord().subscribe({
            next: response => {
              let vaccineString = (response as any).text;

              const regex: RegExp = /\s*([^,(]+)\s*(?:\([^)]+\))?/g;
              let match: RegExpExecArray | null;

              // Iterate through all matches and push them to the vaccinations array
              while ((match = regex.exec(vaccineString)) !== null) {
                const vaccineName = match[1].trim();
                if (vaccineName) {
                  this.vaccinations.push(vaccineName);
                }
              }
            }
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

  suggestedQn(question: string) {
    // Add the selected question as a user message
    this.messages.push({
      role: MessageRole.User,
      message: question
    });

    // Generate a dummy system response
    const dummyResponse = 'Sure, please sign in to your Singpass';
    this.messages.push({
      role: MessageRole.Assistant,
      message: dummyResponse
    });

    // Scroll to the bottom of the message container
    setTimeout(() => {
      this.scrollableTextContent.nativeElement.scrollTop = this.scrollableTextContent.nativeElement.scrollHeight;
    }, 0);
  }

  SingpassLogin() {
    this.isSinpassLogin = true;
  }
}
