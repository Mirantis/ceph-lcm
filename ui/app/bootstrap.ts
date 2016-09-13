import { Component, Input } from '@angular/core';
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

  show(id: string = 'modal') {
    jQuery('#' + id).modal('show');
  }

  close(id: string = 'modal') {
    jQuery('#' + id).modal('hide');
  }
};

@Component({
  selector: 'loader',
  templateUrl: './app/templates/loader.html'
})
export class Loader {};