import { Routes } from '@angular/router';
import { Dashboard } from './components/dashboard/dashboard';
import { Settings } from './components/settings/settings';
import { JsonPad } from './components/json-pad/json-pad';

export const routes: Routes = [
  {
    path: '',
    component: Dashboard
  },
  {
    path: 'json',
    component: JsonPad
  },
  {
    path: 'settings',
    component: Settings
  }
];
