import { Component, Input, Output, EventEmitter, ViewChild, AfterViewInit } from '@angular/core';
import { ErrorService } from './services/error';
import * as jQuery from 'jquery';
import * as _ from 'lodash';
import 'bootstrap';
import globals = require('./services/globals');

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

  isOpened(id: string = 'modal'): boolean {
    return jQuery('#' + id).is(':visible');
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
      if (criterion.value) {
        this.query[criterion.name] = criterion.value;
      } else {
        _.unset(this.query, criterion.name);
      }
    }
    if (this.timeout) {
      window.clearTimeout(this.timeout);
    }
    this.timeout = window.setTimeout(() => this.onChange.emit(), 1000);
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
  @Output() onChange  = new EventEmitter();
  value: string = '';

  handleUpdate(newValue: Object) {
    this.onChange.emit({name: this.name, value: newValue});
  }
}

// Pagination
@Component({
  selector: 'pager',
  templateUrl: './app/templates/pager.html'
})
export class Pager {
  visiblePages = 5;
  page: number = 1;
  @Input() pagingData: {total: number, per_page: number, page: number} = null;
  @Output() onChange  = new EventEmitter();

  getVisiblePages(): number[] {
    let totalPages = Math.ceil(this.pagingData.total / this.pagingData.per_page);
    if (this.page > totalPages) {
      this.switchPage(1);
    }
    let start = this.pagingData.page - Math.round(this.visiblePages / 2);
    if (start < 1) {
      start = 1;
    };
    let finish = start + this.visiblePages;
    if (finish > totalPages) {
      finish = totalPages;
    }
    return _.range(start, finish + 1);
  }

  switchPage(page: number) {
    this.page = page;
    this.onChange.emit();
  }
}

// Long data view
@Component({
  selector: 'longdata',
  template: `<a (click)="expand()" *ngIf="isCollapsed()">{{'{...}'}}</a><span *ngIf="!isCollapsed()"><ng-content></ng-content></span>`
})
export class LongData {
  @Input() key: string;
  @Input() max: number = 50;
  @Input() data: Object = '';
  length: number = 0;

  ngOnInit() {
    this.length = JSON.stringify(this.data).length;
  }

  isCollapsed(): boolean {
    return this.length > this.max && _.get(globals.tempStorage, this.key, true);
  }

  expand() {
    globals.tempStorage[this.key] = false;
  }
}