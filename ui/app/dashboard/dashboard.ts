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

import { Component, EventEmitter } from '@angular/core';
import { AuthService } from '../services/auth';
import { ErrorService } from '../services/error';
import { Modal, Confirmation } from '../directives';

type confirmationData = {confirmation: string, callback: EventEmitter<any>};

@Component({
  templateUrl: './app/templates/dashboard.html'
})
export class DashboardComponent {
  errors: string[] = [];
  confirmationText: string;
  confirmationCallback: EventEmitter<any> = new EventEmitter();

  constructor(
    private auth: AuthService,
    private error: ErrorService,
    private modal: Modal
  ) {
    error.errorHappened.subscribe((error: any) => this.addError(error));
    auth.getLoggedUser();
    Confirmation.bus.subscribe((data: confirmationData) => this.showConfirmation(data));
  }

  hideConfirmation() {
    this.modal.close('confirm');
  }

  showConfirmation(data: confirmationData) {
    this.confirmationText = data.confirmation;
    this.confirmationCallback = data.callback;
    this.modal.show('confirm');
  }

  proceed() {
    this.hideConfirmation();
    this.confirmationCallback.next();
  }

  getLoggedUserName(): string {
    var loggedUser = this.auth.loggedUser;
    return loggedUser && loggedUser.data ? loggedUser.data.full_name : '';
  }

  addError(error: any) {
    if (!this.modal.isOpened()) {
      this.errors.push(error);
    }
  }

  dismissErrors() {
    this.errors = [];
  }

  logout() {
    this.auth.logout().catch(() => true);
  }
}
