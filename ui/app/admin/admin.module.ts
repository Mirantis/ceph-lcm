import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared.module';

import { AdminComponent, UsersComponent,
  RolesComponent, PermissionsGroup } from './index';

@NgModule({
  declarations: [
    AdminComponent,
    UsersComponent,
    RolesComponent,
    PermissionsGroup
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  exports: [
    AdminComponent,
    UsersComponent,
    RolesComponent,
    PermissionsGroup
  ]
})
export class AdminModule { }
