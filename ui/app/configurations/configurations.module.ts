import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { ConfigurationsComponent, WizardComponent, HintComponent } from './index';
import { SharedModule } from '../shared.module';

@NgModule({
  declarations: [
    ConfigurationsComponent,
    WizardComponent,
    HintComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  exports: [
    ConfigurationsComponent,
    WizardComponent,
    HintComponent
  ]
})
export class ConfigurationsModule { }
