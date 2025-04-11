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
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

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

  vaccineSelected: string = '';
  clinicSelected: string = '';
  slotSelected: string = '';

  bookingDate: string = '-';
  bookingTime: string = '-';
  agentUsed: string = '';
  dataType: string = '';
  agentMessage: string = '';
  link: SafeResourceUrl = '';

  isSignUp = false;
  isLoggedIn = false;
  isVaccineSelected = false;
  isClinicSelected = false;
  isBookVaccine: boolean = false;
  isBookingConfirmed: boolean = false;
  isConfirming: boolean = false;
  isLoading: boolean = false;
  hideSlotTable: boolean = false;
  showLogin: boolean = false;
  showLoginButton: boolean = true;
  showConfirmed: boolean = false;
  showBookingSlots: boolean = false;
  showVaccinationRecords: boolean = false;
  showBookingDetails: boolean = false;
  showLinkPreview: boolean = false;
  showClinics: boolean = false;

  greeting: Message[] = [
    {
      role: MessageRole.Assistant,
      message:
        '<b>Welcome to the Beta version of HealthHub AI!</b><br><br>I am your friendly AI assistant, here to help you explore health information on HealthHub. You may ask questions in English, Chinese, Malay, or Tamil.<br><br>My responses may not always be perfect, as I am built on experimental technology and still learning progressively, but I will do my best to assist.<br><br>To ask a question, you can:<br>1. <b>Hold the voice button</b> (🎙️) to speak;<br>2. <b>Type</b> in your question (💬);<br>3. <b>Select from the suggested questions</b>.<br><br>How can I assist you today?<br><br>'
    }
  ];

  suggestedQns: String[] = ['Can you help me book my Vaccination?', 'Please show me my Vaccination history'];
  vaccines: String[] = [];
  clinics: String[] = [];
  messages: Message[] = [];
  vaccinationRecords: String[] = [];
  bookingSlots: string[] = [];
  history: string[] = [];
  userInfo: object = {};

  constructor(
    private toastService: MessageService,
    private endpointService: EndpointService,
    private sanitizer: DomSanitizer
  ) {}

  loginForm: FormGroup = new FormGroup({
    username: new FormControl<string>(''),
    password: new FormControl<string>('')
  });

  signupForm: FormGroup = new FormGroup({
    nric: new FormControl<string>(''),
    first_name: new FormControl<string>(''),
    last_name: new FormControl<string>(''),
    email: new FormControl<string>(''),
    date_of_birth: new FormControl<string>(''),
    gender: new FormControl<string>(''),
    postal_code: new FormControl<string>(''),
    password: new FormControl<string>(''),
    cfm_password: new FormControl<string>('')
  });

  toggleLogin() {
    this.isSignUp = false;
  }

  toggleSignUp() {
    this.isSignUp = true;
  }

  showLoginUI() {
    this.showLogin = true;
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
          this.showLogin = false;
          this.isLoggedIn = true;
          this.isLoading = true;
          this.scrollToBottom();
          if (this.isBookVaccine) {
            this.sendUserRequest('Can you help me book my Vaccination?');
          }
          if (this.showVaccinationRecords) {
            this.sendUserRequest('Please show me my Vaccination history');
          }
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

      this.endpointService.signup(signupData).subscribe({
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

  lastSystemMessage(): Message | null {
    for (let i = this.messages.length - 1; i >= 0; i--) {
      if (this.messages[i].role === MessageRole.Assistant) {
        return this.messages[i];
      }
    }
    return null;
  }

  scrollToBottom() {
    setTimeout(() => {
      this.scrollableTextContent.nativeElement.scrollTop = this.scrollableTextContent.nativeElement.scrollHeight;
    }, 0);
  }

  selectVaccine(vaccine: string) {
    this.isVaccineSelected = true;
    this.vaccineSelected = vaccine;
    this.handleUserInput(vaccine); // pass the vaccine text to chat input
  }

  selectClinic(clinic: string) {
    this.clinicSelected = clinic;
    this.showClinics = false;
    this.handleUserInput(clinic); // pass the clinic text to chat input
  }

  selectSlot(slot: string) {
    this.slotSelected = slot;
    this.bookingDate = slot.substring(0, slot.indexOf(','));
    this.bookingTime = slot.substring(slot.indexOf(',') + 2);
    this.isConfirming = true;
    this.showBookingDetails = true;
    this.showBookingSlots = false;
    this.messages.push({
      role: MessageRole.Assistant,
      message: 'Please confirm your booking date and time: ' + this.bookingDate + ' ' + this.bookingTime
    });
  }

  confirmSelectedSlot() {
    this.sendUserRequest(this.slotSelected);
    this.isConfirming = false;
  }

  clearState() {
    this.showLoginButton = false;
    this.isBookVaccine = false;
    this.isConfirming = false;
    this.showBookingSlots = false;
    this.showVaccinationRecords = false;
    this.isBookingConfirmed = false;
    this.showConfirmed = false;
    this.showBookingDetails = false;
    this.isVaccineSelected = false;
    this.isClinicSelected = false;
    this.showLinkPreview = false;
    this.showClinics = false;
  }

  handleUserInput(message: string): void {
    // Add the user message to the messages array
    this.isLoading = true;
    this.messages.push({
      role: MessageRole.User,
      message: message
    });
    if (!this.isLoggedIn && this.suggestedQns.includes(message)) {
      this.messages.push({
        role: MessageRole.Assistant,
        message: 'To proceed, please log in to your account'
      });
      this.isLoading = false;
      this.isBookVaccine = message.trim() === this.suggestedQns[0];
      this.showVaccinationRecords = message.trim() === this.suggestedQns[1];
      this.showLoginButton = this.isBookVaccine || this.showVaccinationRecords;
      this.scrollToBottom();
    } else {
      this.sendUserRequest(message);
    }
  }

  sendUserRequest(message: string) {
    this.endpointService.sendMessageToOrchestrator(message, this.history, this.agentUsed, this.userInfo).subscribe({
      next: response => {
        this.isLoading = false;
        if (!response) {
          this.toastService.add({
            severity: 'error',
            summary: 'Server Error',
            detail: 'No response received from the server'
          });
          return;
        }

        this.agentUsed = response.agent_name;
        this.clearState();

        // Based on data_type, handle the display of components differently
        switch (response.data_type) {
          case 'vaccine_record':
            this.vaccinationRecords = response.data.vaccines;
            this.showVaccinationRecords = true;
            break;
          case 'vaccine_list':
            let vaccineList: any[];
            vaccineList = JSON.parse(response.data);
            this.showBookingDetails = true;
            this.vaccines = vaccineList.map((vaccine: any) => vaccine.name);
            this.isBookVaccine = true;
            break;
          case 'clinic_list':
            let clinicList: any[];
            clinicList = JSON.parse(response.data);
            this.showBookingDetails = true;
            this.clinics = clinicList.map((clinic: any) => clinic.name);
            this.showClinics = true;
            break;
          case 'booking_slots':
            let slots: any[];
            slots = JSON.parse(response.data);
            this.bookingSlots = slots.map((slot: any) => {
              const date = new Date(slot.datetime);
              const options: Intl.DateTimeFormatOptions = {
                year: 'numeric', // e.g., 2025
                month: 'long', // e.g., March
                day: 'numeric', // e.g., 3
                hour: '2-digit', // e.g., 09
                minute: '2-digit', // e.g., 00
                hour12: true // e.g., AM/PM format
              };
              return date.toLocaleString('en-US', options);
            });
            this.showBookingSlots = true;
            this.showBookingDetails = true;
            break;
          case 'booking_details':
            let bookingDetails: any;
            bookingDetails = JSON.parse(response.data);
            this.vaccineSelected = bookingDetails.vaccine;
            this.clinicSelected = bookingDetails.clinic;
            this.bookingDate = bookingDetails.date;
            this.bookingTime = bookingDetails.time;
            this.isBookingConfirmed = true;
            this.showBookingDetails = true;
            break;
          case 'booking_success':
            this.vaccineSelected = response.data.vaccine;
            this.clinicSelected = response.data.clinic;
            this.bookingDate = response.data.date;
            this.bookingTime = response.data.time;
            this.isBookingConfirmed = true;
            this.showConfirmed = true;
            this.showBookingDetails = true;
            break;
          case 'general_query_response':
            this.link = this.sanitizer.bypassSecurityTrustResourceUrl(response.data.link);
            this.showLinkPreview = true;
            break;
          default:
            // just display response.message
            break;
        }

        this.history = response.history;
        this.userInfo = response.user_info;

        this.messages.push({
          role: MessageRole.Assistant,
          message: response.message
        });

        this.scrollToBottom();
      },
      error: err => {}
    });
  }
}
