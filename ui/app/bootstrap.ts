import { Component, Input } from '@angular/core';
import { ErrorService } from './services/error';
import * as jQuery from 'jquery';
import 'bootstrap';

@Component({
  selector: 'modal',
  templateUrl: './app/templates/bootstrap_modal.html'
})
export class Modal {
  @Input() id: string = 'modal';
  @Input() title: string = '';
  @Input() isLarge: boolean = false;

  errors: {error: string, message: string}[] = [];

  constructor(private error: ErrorService) {
    error.errorHappened.subscribe((error: any) => this.addError(error));
  }

  show(id: string = 'modal') {
    jQuery('#' + id).modal('show');
  }

  close(id: string = 'modal') {
    jQuery('#' + id).modal('hide');
  }

  addError(error: any) {
    this.errors.push(error);
  }

  dismissErrors() {
    this.errors = [];
  }

  isOpened(): boolean {
    return jQuery('modal').is(':visible');
  }
};

@Component({
  selector: 'loader',
  templateUrl: './app/templates/loader.html'
})
export class Loader {};