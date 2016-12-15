import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import {
  ConfigurationsComponent, WizardComponent, HintComponent,
  WizardStepContainer, NameAndClusterStep, PlaybookStep, HintsStep, ServersStep
} from './index';
import { WizardService } from '../services/wizard';
import { SharedModule } from '../shared.module';

@NgModule({
  declarations: [
    ConfigurationsComponent,
    WizardComponent,
    WizardStepContainer, NameAndClusterStep, PlaybookStep, HintsStep, ServersStep,
    HintComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  entryComponents: [
    NameAndClusterStep, PlaybookStep, HintsStep, ServersStep
  ],
  providers: [
    WizardService
  ],
  exports: [
    ConfigurationsComponent,
    WizardComponent,
    WizardStepContainer, NameAndClusterStep, PlaybookStep, HintsStep, ServersStep,
    HintComponent
  ]
})
export class ConfigurationsModule { }
