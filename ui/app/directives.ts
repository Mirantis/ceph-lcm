import { Component, Input, Output, EventEmitter } from '@angular/core';
import { ErrorService } from './services/error';
import * as jQuery from 'jquery';
import * as _ from 'lodash';
import 'bootstrap';

// Bootstrap modal methods
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
    if (_.isEmpty(error)) {
      this.errors = [];
    } else {
      this.errors.push(error);
    }
  }

  dismissErrors() {
    this.errors = [];
  }

  isOpened(): boolean {
    return jQuery('modal').is(':visible');
  }
};

// Rotating shrimp loading indicator
@Component({
  selector: 'loader',
  templateUrl: './app/templates/loader.html'
})
export class Loader {};

type CriterionType = {name: string, value: string};

// Filter control
@Component({
  selector: 'filter',
  templateUrl: './app/templates/filter.html'
})
export class Filter {
  @Input() criteria: Object = {};
  @Output() onChange = new EventEmitter();
  query: Object = {};
  timeout: number;

  getCriteriaOffset() {
    let criteriaCount = _.keys(this.criteria).length;
    return 10 - criteriaCount * 3;
  }

  criterionUpdated(criterion: CriterionType|string) {
    if (typeof criterion === 'string') {
      this.query['name'] = {'regexp': criterion};
    } else {
      this.query[criterion.name] = criterion.value;
    }
    if (this.timeout) {
      window.clearTimeout(this.timeout);
    }
    this.timeout = window.setTimeout(() => this.onChange.emit(this.query), 1000);
  }
}

// Filtering criterion
@Component({
  selector: 'criterion',
  templateUrl: './app/templates/filtering_criterion.html'
})
export class Criterion {
  @Input() name: string = '';
  @Input() values: string[] = [];
  @Output() updateHandler  = new EventEmitter();
  value: string = '';

  onChange(newValue: Object) {
    this.updateHandler.emit({name: this.name, value: newValue});
  }
}