import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { WizardComponent } from './wizard';
import { WizardStepContainer, TestWizardStep } from './wizard_step';

import { Modal, Loader, Filter, Criterion, Pager, LongData } from './directives';
import { Key, Keys, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix } from './pipes';

@NgModule({
  imports: [
    BrowserModule, FormsModule
  ],
  declarations: [
    Modal, Loader, Filter, Criterion, Pager, LongData,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix,
    WizardComponent, WizardStepContainer, TestWizardStep
  ],
  exports: [
    Modal, Loader, Filter, Criterion, Pager, LongData,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix,
    WizardComponent, WizardStepContainer, TestWizardStep
  ],
  entryComponents: [
    TestWizardStep
  ],
  providers: [
    Modal, Loader, Filter, Criterion, Pager, LongData
  ]
})
export class SharedModule { }
