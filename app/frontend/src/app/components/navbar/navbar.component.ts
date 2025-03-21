import { Component, OnInit } from '@angular/core';
import { SidebarModule } from 'primeng/sidebar';
import { CommonModule } from '@angular/common';
import { TagModule } from 'primeng/tag';
import { DropdownModule } from 'primeng/dropdown';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NavbarLineComponent } from '../navbar-line/navbar-line.component';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, SidebarModule, TagModule, DropdownModule, FormsModule, ReactiveFormsModule, NavbarLineComponent],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit {
  sidebar: boolean = false;
  firstLoad: boolean = true;
  body: any = 'body';
  languageMap = [
    { name: 'As Spoken', value: 'Spoken' },
    { name: 'English', value: 'English' },
    { name: '中文', value: 'Chinese' },
    { name: 'Melayu', value: 'Malay' },
    { name: 'தமிழ்', value: 'Tamil' }
  ];
  chosenLanguage!: string;
  chosenNativeLanguage!: string;

  ngOnInit() {
    this.languageMap = this.languageMap.filter(l => l.value !== 'Spoken');
  }

  toggleSidebar() {
    this.sidebar = !this.sidebar;
    this.firstLoad = false;
  }

  closeSidebar() {
    //clicking
    this.sidebar = false;
  }

  setLanguage(chosenLanguage: string) {
    switch (chosenLanguage) {
      case 'English':
        // this.preferences.setLanguage(Language.English);
        // this.languageService.setLanguage(Language.English);
        this.chosenNativeLanguage = 'English';
        break;

      // case "Spoken":
      //   this.preferences.setLanguage(Language.Spoken);
      //   this.chosenNativeLanguage = "Spoken";
      //   break;

      case 'Chinese':
        // this.preferences.setLanguage(Language.Chinese);
        // this.languageService.setLanguage(Language.Chinese);
        this.chosenNativeLanguage = '中文';
        break;

      case 'Malay':
        // this.preferences.setLanguage(Language.Malay);
        // this.languageService.setLanguage(Language.Malay);
        this.chosenNativeLanguage = 'Melayu';
        break;

      case 'Tamil':
        // this.preferences.setLanguage(Language.Tamil);
        // this.languageService.setLanguage(Language.Tamil);
        this.chosenNativeLanguage = 'தமிழ்';
        break;
      default:
        break;
    }
  }

  getNativeLanguage(language: string) {
    switch (language) {
      case 'English':
        return 'English';
      case 'Chinese':
        return '中文';
      case 'Malay':
        return 'Melayu';
      case 'Tamil':
        return 'தமிழ்';
      default:
        return 'English';
    }
  }

  // openUserGuide(): void {
  //   this.userGuide.open();
  // }

  // openFeedback(): void {
  //   this.feedbackModal.open();
  // }

  // closeFeedback(): void {
  //   this.feedbackModal.close();
  // }

  // protected readonly GeneralPersona = GeneralPersona;
  // protected readonly ChatMode = ChatMode;
}
