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

import { Component, Directive, Input, Output, EventEmitter, ViewChild,
  AfterViewInit, HostListener } from '@angular/core';
import { ErrorService } from './services/error';
import * as jQuery from 'jquery';
import * as _ from 'lodash';
import 'bootstrap';
import globals = require('./services/globals');
import { BaseModel } from './models';

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
    jQuery('#' + id).modal({backdrop: 'static', show: true});
  }

  isExpanded() {
    return jQuery('#modal-dialog').hasClass('modal-lg');
  }

  toggleLarge() {
    jQuery('#modal-dialog').toggleClass('modal-lg');
  }

  close(id: string = 'modal') {
    jQuery('#' + id).modal('hide');
    if (this.isExpanded() !== this.isLarge) {
      setTimeout(this.toggleLarge, 500);
    }
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

// Rotating decapod loading indicator
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
  @Input() pagingData: {total: number, per_page: number, page: number} = null;
  @Input() isHidden: boolean = false;
  @Output() onChange  = new EventEmitter();

  public get page(): number {
    return +this.pagingData.page || 1;
  }

  public get perPage(): number {
    return +this.pagingData.per_page || 25;
  }

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
    this.onChange.emit(page);
  }

  getPageItems(allItems: BaseModel[]): BaseModel[] {
    return _.slice(allItems, (this.page - 1) * this.perPage, this.perPage);
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

@Directive({
  selector: '[confirmedClick]'
})
export class Confirmation {
  static bus = new EventEmitter();

  @Input() confirmation = 'Are you sure?';
  @Output() confirmedClick = new EventEmitter();
  @HostListener('click', ['$event']) onClick(e: any) {
    Confirmation.bus.emit({confirmation: this.confirmation, callback: this.confirmedClick});
  }
}
