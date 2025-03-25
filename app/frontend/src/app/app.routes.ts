import { Routes } from '@angular/router';
import { MainLayoutComponent } from './layouts/main-layout/main-layout.component';
import { VaccineIndexComponent } from './components/vaccine-index/vaccine-index.component';

export const routes: Routes = [{ path: "",
    title: "HealthHub AI",
    component: MainLayoutComponent,
 children: [
      {
        path: "",
        children: [
 {path: "",
            component: VaccineIndexComponent
 }


        ]}]
}
, {
    path: "**",
    component: VaccineIndexComponent
  }
];
