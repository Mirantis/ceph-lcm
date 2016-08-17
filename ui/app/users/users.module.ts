import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { AdminComponent, UsersComponent, RolesComponent } from './index';
import { Keys } from '../pipes';

@NgModule({
  declarations: [
    AdminComponent,
    UsersComponent,
    RolesComponent,
    Keys
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule
  ],
  exports: [
    AdminComponent,
    UsersComponent,
    RolesComponent
  ]
})
export class UsersModule { }
