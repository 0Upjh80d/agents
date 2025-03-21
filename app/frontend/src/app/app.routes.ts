import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { ChatComponent } from './components/chat/chat.component';

export const routes: Routes = [
  {
    path: '',
    title: 'Vaccine AI',
    component: MainLayoutComponent,
    children: [
      { path: '', pathMatch: 'full', redirectTo: '/chat' },
      {
        path: '',
        children: [{ path: 'chat', pathMatch: 'full', component: ChatComponent }]
      }
    ]
  }
];
