import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { Settings } from './components/settings/settings';

export const routes: Routes = [
  {
    path: '',
    component: Dashboard
  },
  {
    path: 'settings',
    component: Settings
  }
];
