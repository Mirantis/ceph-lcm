import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import {
  ConfigurationsComponent, WizardComponent, HintComponent,
  WizardStepContainer
} from './index';

import { NameAndClusterStep, PlaybookStep, HintsStep, ServersStep, JsonConfigurationStep } from './wizard_steps/index';
import { WizardService } from '../services/wizard';
import { SharedModule } from '../shared.module';

@NgModule({
  declarations: [
    ConfigurationsComponent,
    WizardComponent,
    WizardStepContainer, NameAndClusterStep, PlaybookStep, HintsStep, ServersStep, JsonConfigurationStep,
    HintComponent
  ],
  imports: [
    BrowserModule,
    RouterModule,
    FormsModule,
    SharedModule
  ],
  entryComponents: [
    NameAndClusterStep, PlaybookStep, HintsStep, ServersStep, JsonConfigurationStep
  ],
  providers: [
    WizardService
  ],
  exports: [
    ConfigurationsComponent,
    WizardComponent,
    WizardStepContainer, NameAndClusterStep, PlaybookStep, HintsStep, ServersStep, JsonConfigurationStep,
    HintComponent
  ]
})
export class ConfigurationsModule { }
