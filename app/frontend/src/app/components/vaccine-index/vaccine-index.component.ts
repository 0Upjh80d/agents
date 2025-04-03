import { CommonModule } from '@angular/common';
import { AfterViewChecked, Component, ElementRef, ViewChild } from '@angular/core';
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

  vaccineSelected: string = '';
  bookingDate: string = '-';
  bookingTime: string = '-';
  agentUsed: string = '';

  isSignUp = false;
  isSinpassLogin = false;
  isLoggedIn = false;
  isVaccineSelected = false;
  isBookVaccine: boolean = false;
  isBookingConfirmed: boolean = false;
  isConfirming: boolean = false;
  hideSlotTable: boolean = false;
  showConfirmed: boolean = false;

  greeting: Message[] = [
    {
      role: MessageRole.Assistant,
      message:
        '<b>Welcome to the Beta version of HealthHub AI!</b><br><br>I am your friendly AI assistant, here to help you explore health information on HealthHub. You may ask questions in English, Chinese, Malay, or Tamil.<br><br>My responses may not always be perfect, as I am built on experimental technology and still learning progressively, but I will do my best to assist.<br><br>To ask a question, you can:<br>1. <b>Hold the voice button</b> (🎙️) to speak;<br>2. <b>Type</b> in your question (💬);<br>3. <b>Select from the suggested questions</b>.<br><br>How can I assist you today?<br><br>'
    }
  ];

  suggestedQns: String[] = ['Can you help me book my Vaccination?', 'Please show me my Vaccination history'];
  vaccines: String[] = ['Pneumococcal conjugate 13-valent (PCV-13)', 'Varicella (VAR)', 'Influenza (trivalent) (INF)', 'Hepatitis B (HepB)'];
  messages: Message[] = [];
  vaccinationRecords: String[] = [];
  constructor(
    private toastService: MessageService,
    private endpointService: EndpointService
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
                  this.vaccinationRecords.push(vaccineName);
                }
              }
            }
          });
          this.scrollToBottom();
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

    let dummyResponse = 'Sure, please sign in to your Singpass';

    if (this.isLoggedIn) dummyResponse = 'Sure';

    this.isBookVaccine = question.trim() === this.suggestedQns[0].trim();

    // Generate a dummy system response
    this.messages.push({
      role: MessageRole.Assistant,
      message: dummyResponse
    });
    this.scrollToBottom();
  }

  SingpassLogin() {
    this.agentUsed = 'Login agent';
    this.isSinpassLogin = true;
  }

  lastSystemMessage(): Message | null {
    for (let i = this.messages.length - 1; i >= 0; i--) {
      if (this.messages[i].role === MessageRole.Assistant) {
        return this.messages[i];
      }
    }
    return null;
  }

  // Scroll to the bottom of the message container
  scrollToBottom() {
    setTimeout(() => {
      this.scrollableTextContent.nativeElement.scrollTop = this.scrollableTextContent.nativeElement.scrollHeight;
    }, 0);
  }

  selectVaccine(v: string) {
    this.isVaccineSelected = true;
    this.hideSlotTable = false;

    this.vaccineSelected = v;

    this.agentUsed = 'Booking agent';

    this.messages.push({
      role: MessageRole.User,
      message: v
    });

    this.messages.push({
      role: MessageRole.Assistant,
      message: 'Please tell me the date and time you wanted to book the vaccine?'
    });
    this.scrollToBottom();
  }

  handleUserInput(message: string): void {
    // Add the user message to the messages array
    this.messages.push({
      role: MessageRole.User,
      message: message
    });

    // Process the message to generate a response
    this.processUserInput(message);
    this.scrollToBottom();
  }

  processUserInput(message: string): void {
    if (message === 'Confirm') {
      this.isConfirming = false;
      this.isBookingConfirmed = true;

      this.messages.push({
        role: MessageRole.User,
        message: message
      });

      this.messages.push({
        role: MessageRole.Assistant,
        message: `Your appointment for ${this.vaccineSelected} has been booked for ${this.bookingTime} at ${this.bookingDate}. Please arrive 15 minutes before your appointment.`
      });
      this.scrollToBottom();
      this.isBookVaccine = false;
      setTimeout(() => {
        this.showConfirmed = true;
      }, 2000);
      return;
    }
    // Check if the message contains date and time information (for vaccine booking)
    if (this.isBookVaccine) {
      const dateTimeInfo = this.extractDateAndTime(message);
      // Generate a response based on the date and time
      if (dateTimeInfo.dateString && dateTimeInfo.timeString) {
        this.hideSlotTable = true;

        this.bookingDate = dateTimeInfo.dateString;
        this.bookingTime = dateTimeInfo.timeString;
        this.isConfirming = true;
        this.messages.push({
          role: MessageRole.Assistant,
          message: 'Do you want to confirm your booking?'
        });
        this.isBookVaccine = false;
      } else {
        this.messages.push({
          role: MessageRole.Assistant,
          message: `I couldn't recognize the date and time in your message. Please specify a date (e.g., "28 Mar") and time (e.g., "2pm") for your appointment.`
        });
      }
    } else {
      // Generic response for other queries
      this.messages.push({
        role: MessageRole.Assistant,
        message: 'I understand you asked about: "' + message + '". How else can I assist you with your health information today?'
      });
    }
  }

  // Extract date and time from user input
  extractDateAndTime(input: string): { dateString: string; timeString: string } {
    // Initialize result
    let dateString = '';
    let timeString = '';

    // Convert to lowercase and remove extra spaces
    const text = input.toLowerCase().trim().replace(/\s+/g, ' ');

    // Regular expressions for date patterns
    const datePattern = /\b(\d{1,2})(?:\s*)(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b/;

    // Regular expressions for time patterns
    const timePattern = /\b(\d{1,2})(?::(\d{2}))?(?:\s*)?(am|pm)?\b/;

    // Extract date
    const dateMatch = text.match(datePattern);
    if (dateMatch) {
      const day = parseInt(dateMatch[1]);
      const month = dateMatch[2];

      // Map month abbreviation to full month name
      const monthMap: { [key: string]: string } = {
        jan: 'January',
        feb: 'February',
        mar: 'March',
        apr: 'April',
        may: 'May',
        jun: 'June',
        jul: 'July',
        aug: 'August',
        sep: 'September',
        oct: 'October',
        nov: 'November',
        dec: 'December'
      };

      const fullMonth = monthMap[month];
      dateString = `${day} ${fullMonth} 2025`;
    }

    // Extract time
    const timeMatch = text.match(timePattern);
    if (timeMatch) {
      let hours = parseInt(timeMatch[1]);
      const minutes = timeMatch[2] ? parseInt(timeMatch[2]) : 0;
      const period = timeMatch[3] ? timeMatch[3].toLowerCase() : hours < 12 ? 'am' : 'pm'; // Default to am/pm based on hour

      // Format time string
      const formattedHours = hours % 12 === 0 ? 12 : hours % 12;
      const ampm = period === 'pm' || (period !== 'am' && hours >= 12) ? 'PM' : 'AM';
      timeString = `${formattedHours}:${minutes.toString().padStart(2, '0')} ${ampm}`;
    }

    return { dateString, timeString };
  }
}
