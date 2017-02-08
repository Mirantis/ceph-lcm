/**
* Copyright (c) 2016 Mirantis Inc.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
* implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*/

import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { BrowserModule } from '@angular/platform-browser';

import { WizardComponent } from './wizard';
import { WizardStepContainer, TestWizardStep } from './wizard_step';

import { Modal, Loader, Filter, Criterion, Pager, LongData, Confirmation } from './directives';
import { Key, Keys, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix } from './pipes';

@NgModule({
  imports: [
    BrowserModule, FormsModule
  ],
  declarations: [
    Modal, Loader, Filter, Criterion, Pager, LongData,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix,
    WizardComponent, WizardStepContainer, TestWizardStep,
    Confirmation
  ],
  exports: [
    Modal, Loader, Filter, Criterion, Pager, LongData,
    Keys, Key, TrimBy, DateTime, JSONString, Index, Deparametrize, Deprefix,
    WizardComponent, WizardStepContainer, TestWizardStep,
    Confirmation
  ],
  entryComponents: [
    TestWizardStep
  ],
  providers: [
    Modal, Loader, Filter, Criterion, Pager, LongData, Confirmation
  ]
})
export class SharedModule { }
