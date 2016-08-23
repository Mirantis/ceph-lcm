import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SharedModule } from '../shared.module';

import { AdminComponent, UsersComponent, RolesComponent } from './index';

@NgModule({
  declarations: [
    AdminComponent,
    UsersComponent,
    RolesComponent
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
    RolesComponent
  ]
})
export class AdminModule { }
